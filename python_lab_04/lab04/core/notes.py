from collections import Counter
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, replace
from hashlib import sha256
from itertools import chain, islice
from os import getpid
from random import Random
from secrets import randbits
from threading import Event

from .errors import InputError, check_cancelled, check_range

# Параметры генерации: допустимые ноты, ограничения,
# размер пакетов и настройки вычислительной нагрузки.
NOTES = ("до", "ре", "ми", "фа", "соль", "ля", "си")
NOTE_BYTES = {note: note.encode() for note in NOTES} # ноты, переведенные в байты
PREVIEW_SIZE = 20
DEFAULT_COUNT = 1_000_000
MAX_COUNT = 100_000_000
DEFAULT_BATCH_SIZE = 4096 # сколько нот за одну порцию, т.е. миллион где-то на 245 пакетов
MAX_BATCH_SIZE = 16_384
MAX_ROUNDS = 256 # максимальное количество вычислеий SHA-256 для каждой ноты в загрузочном режиме
CHECKSUM_MASK = (1 << 64) - 1 # ограничиваем итоговую контрольную сумму 64 битами
Progress = Callable[[int, int], None]

# Неизменяемая конфигурация одного запуска.
# Проверяет параметры и обеспечивает воспроизводимость через seed.
@dataclass(frozen=True)
class NotesConfig:
    count: int = DEFAULT_COUNT
    seed: int | None = None
    batch_size: int = DEFAULT_BATCH_SIZE
    rounds: int = 0

    # проверка на допустимые значения
    def __post_init__(self) -> None:
        check_range(self.count, 1, MAX_COUNT, "Количество нот")
        check_range(self.batch_size, 1, MAX_BATCH_SIZE, "Размер пакета")
        check_range(self.rounds, 0, MAX_ROUNDS, "Итерации SHA-256 на ноту")
        if self.seed is not None and type(self.seed) is not int:
            raise InputError("Seed должен быть целым числом. Пустое поле выбирает случайное зерно.")


    def with_seed(self) -> "NotesConfig":
        return self if self.seed is not None else replace(self, seed=randbits(64))

    @property
    def batch_count(self) -> int:
        return (self.count + self.batch_size - 1) // self.batch_size

# Задание на обработку одного пакета
@dataclass(frozen=True)
class Batch:
    count: int
    seed: int
    rounds: int


# Результат обработки пакета
@dataclass(frozen=True)
class NoteSummary:
    count: int
    preview: tuple[str, ...]
    frequencies: tuple[int, ...]
    checksum: int

# Окончательный результат генерации
@dataclass(frozen=True)
class GenerationResult:
    summary: NoteSummary
    process_ids: frozenset[int]


# Лениво выдаёт случайные ноты по одной.
# При одинаковом seed последовательность воспроизводима.
def random_notes(count: int = DEFAULT_COUNT, seed: int | None = None) -> Iterator[str]:
    check_range(count, 1, MAX_COUNT, "Количество нот")
    if seed is not None and type(seed) is not int:
        raise InputError("Seed должен быть целым числом.")
    choice = Random(seed).choice
    for _ in range(count):
        yield choice(NOTES) # генератор выдаёт ноты постепенно


# Лениво делит общую генерацию на пакеты.
# Каждому пакету назначается независимый, воспроизводимый seed.
def iter_batches(config: NotesConfig) -> Iterator[Batch]:
    # Random(config.seed) воспроизводит последовательность seed для пакетов.
    # Поэтому результат пакета не зависит от того, какой процесс его выполнит.
    seeds = Random(config.seed)
    for start in range(0, config.count, config.batch_size):
        yield Batch(min(config.batch_size, config.count - start), seeds.getrandbits(128), config.rounds)

# Обрабатывает один пакет: сохраняет первые 20 нот,
# подсчитывает частоты и при необходимости выполняет SHA-256.
# Возвращает компактную сводку и PID процесса.
def process_batch(batch: Batch) -> tuple[NoteSummary, int]:
    notes = random_notes(batch.count, batch.seed)
    preview = tuple(islice(notes, PREVIEW_SIZE))
    stream = chain(preview, notes)
    checksum = 0
    # Counter последовательно потребляет генератор и считает частоты нот. Все элементы заранее в памяти не сохраняются.
    frequencies = Counter()
    # Нагрузочный режим: многократно хешируем каждую ноту через SHA-256.
    # Используем результат для контрольной суммы и отдельно считаем частоты.
    # Это позволяет сравнивать последовательные и параллельные вычисления.
    if batch.rounds:
        rounds = range(batch.rounds)
        for note in stream:
            value = NOTE_BYTES[note]
            for _ in rounds:
                value = sha256(value).digest()
            checksum += int.from_bytes(value[:8], "big")
            frequencies[note] += 1
    else:
        frequencies.update(stream)
    summary = NoteSummary(batch.count, preview, tuple(frequencies[note] for note in NOTES), checksum & CHECKSUM_MASK)
    return summary, getpid()


# Последовательно обрабатывает пакеты в текущем процессе.
# Перед каждым пакетом проверяет запрос на отмену.
def sequential_batches(config: NotesConfig, cancel: Event | None = None) -> Iterator[tuple[NoteSummary, int]]:
    for batch in iter_batches(config):
        check_cancelled(cancel)
        yield process_batch(batch)

# Объединяет результаты всех пакетов в одну сводку.
# Проверяет целостность подсчёта и обновляет прогресс.
def collect_results(batches: Iterable[tuple[NoteSummary, int]], total: int, cancel: Event | None = None, progress: Progress | None = None,
) -> GenerationResult:
    count = checksum = 0
    frequencies = [0] * len(NOTES)
    preview: list[str] = []
    process_ids: set[int] = set()
    for summary, pid in batches:
        check_cancelled(cancel)
        count += summary.count
        preview.extend(summary.preview[:PREVIEW_SIZE - len(preview)])
        frequencies = [current + extra for current, extra in zip(frequencies, summary.frequencies, strict=True)]
        checksum += summary.checksum
        process_ids.add(pid)
        if progress is not None:
            progress(count, total)
    check_cancelled(cancel)
    if count != total or sum(frequencies) != total:
        raise RuntimeError("Количество нот и сумма частот должны совпадать с заданным объёмом.")
    summary = NoteSummary(count, tuple(preview), tuple(frequencies), checksum & CHECKSUM_MASK)
    return GenerationResult(summary, frozenset(process_ids))
