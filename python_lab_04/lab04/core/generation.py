from dataclasses import dataclass
from enum import StrEnum
from threading import Event
from time import perf_counter

from .notes import GenerationResult, NotesConfig, Progress, collect_results, sequential_batches
from .parallel import note_pool, parallel_batches, workers_for


# Режимы выполнения. label преобразует значение режима в название для отображения в интерфейсе.
class Mode(StrEnum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"

    @property
    def label(self) -> str:
        return "Последовательный" if self is Mode.SEQUENTIAL else "Параллельный"


# Итог одного запуска: результаты генерации, использованный seed, затраченное время и количество рабочих процессов.
@dataclass(frozen=True)
class NoteRun:
    result: GenerationResult
    seed: int
    seconds: float
    pool_workers: int


def run_notes(config: NotesConfig, mode: Mode, workers: int = 1, cancel: Event | None = None, progress: Progress | None = None,
) -> NoteRun:
    # Если seed не задан, создаём случайный для текущего запуска.
    # perf_counter() запоминает начальное показание таймера.
    config = config.with_seed()
    assert config.seed is not None
    started = perf_counter()

    # Выбираем способ выполнения пакетов. В обоих режимах результаты объединяет collect_results().
    if mode is Mode.PARALLEL:
        workers = workers_for(config, workers)
        with note_pool(workers, cancel) as (executor, _):
            batches = parallel_batches(config, executor, workers, cancel)
            result = collect_results(batches, config.count, cancel, progress)
    else:
        workers = 1
        result = collect_results(sequential_batches(config, cancel), config.count, cancel, progress)

    # Возвращаем результат и полное время выполнения. Для параллельного режима оно включает создание пула процессов.
    return NoteRun(result, config.seed, perf_counter() - started, workers)
