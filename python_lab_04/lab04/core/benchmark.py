from contextlib import nullcontext
from dataclasses import dataclass
from statistics import median
from threading import Event
from time import perf_counter

from .errors import check_range
from .generation import Mode
from .notes import NotesConfig, Progress, collect_results, sequential_batches
from .parallel import note_pool, parallel_batches, workers_for

DEFAULT_REPEATS = 3
DEFAULT_CPU_COUNT = 100_000
DEFAULT_CPU_ROUNDS = 64
MAX_REPEATS = 9

# Хранит отдельные замеры одного режима. Для сравнения используем медиану.
@dataclass(frozen=True)
class Measurements:
    mode: Mode
    samples: tuple[float, ...]
    process_count: int

    @property
    def median_seconds(self) -> float:
        return median(self.samples)


@dataclass(frozen=True)
class BenchmarkResult:
    sequential: Measurements | None
    parallel: Measurements | None
    pool_setup_seconds: float
    pool_workers: int
    seed: int

    # Вычисление ускорения (последовательно / параллельно)
    # Если > 1, значит параллельный режим выигрывает.
    @property
    def speedup(self) -> float | None:
        if self.sequential is None or self.parallel is None:
            return None
        return self.sequential.median_seconds / self.parallel.median_seconds

    @property
    def time_saved_percent(self) -> float | None:
        speedup = self.speedup
        return None if speedup is None else 100 * (1 - 1 / speedup)

    @property
    def explanation(self) -> str:
        saved = self.time_saved_percent
        if saved is None:
            return "Для расчёта ускорения запустите оба режима."
        if abs(saved) < 1:
            return "Медианы различаются меньше чем на 1 %. При повторном запуске порядок может измениться."
        if saved > 0:
            return "Пул сократил время этого прогона. При разовом запуске учитывайте также запуск процессов."
        return "В этом прогоне пул занял больше времени. Передача пакетов, планирование и доступное число ядер влияют на итог."


def compare(
    config: NotesConfig,
    workers: int,
    repeats: int = DEFAULT_REPEATS,
    mode: Mode | None = None,
    cancel: Event | None = None,
    progress: Progress | None = None,
) -> BenchmarkResult:

    check_range(repeats, 1, MAX_REPEATS, "Количество повторов")
    config = config.with_seed()
    assert config.seed is not None

    modes = tuple(Mode) if mode is None else (mode,)
    use_pool = Mode.PARALLEL in modes
    workers = workers_for(config, workers) if use_pool else 0

    timings: dict[Mode, list[float]] = {item: [] for item in modes} # времена отдельных запусков
    process_ids: dict[Mode, set[int]] = {item: set() for item in modes} # идентификаторы процессов

    # общий прогресс
    total = len(modes) * (repeats + 1) * config.count
    finished = 0

    reference = None

    # функция обратного вызова для прогресс-бара
    # Общий прогресс учитывает все запуски, включая прогрев.
    def report(count: int, _: int) -> None:
        if progress is not None:
            # count - сколько нот обработано в текущем запуске
            # finished - сколько нот обработано в завершенных запусках
            progress(finished + count, total)

    # Создаём пул один раз для всего эксперимента.
    # При последовательном режиме используем пустой контекст.
    # Время запуска пула измеряем отдельно.
    pool = note_pool(workers, cancel) if use_pool else nullcontext((None, 0.0))

    with pool as (executor, setup_seconds):
        for iteration in range(repeats + 1):

            # Первый повтор — прогрев, остальные — измерения.

            # На чётных итерациях запускаем режимы в прямом порядке,
            # на нечётных — в обратном, уменьшая влияние порядка запуска. - Чередуются
            for current in modes if iteration % 2 == 0 else reversed(modes):
                if current is Mode.PARALLEL:
                    assert executor is not None
                    batches = parallel_batches(config, executor, workers, cancel)
                else:
                    batches = sequential_batches(config, cancel)

                started = perf_counter()
                result = collect_results(batches, config.count, cancel, report if progress is not None else None)
                elapsed = perf_counter() - started
                finished += config.count

                # Сохраняем результат первого запуска как эталон.
                # Все следующие запуски должны возвращать такую же сводку.
                if reference is None:
                    reference = result.summary
                elif result.summary != reference:
                    raise RuntimeError("Прогоны с одинаковыми параметрами дали разные результаты.")
                if iteration > 0:
                    timings[current].append(elapsed)
                    process_ids[current].update(result.process_ids)

    # Прогрев не включаем в статистику.
    # Сохраняем времена измеряемых запусков и PID процессов.
    measurements = {
        item: Measurements(item, tuple(timings[item]), len(process_ids[item])) for item in modes
    }
    return BenchmarkResult(
        measurements.get(Mode.SEQUENTIAL), measurements.get(Mode.PARALLEL), setup_seconds, workers, config.seed
    )
