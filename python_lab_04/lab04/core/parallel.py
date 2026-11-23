import multiprocessing as mp
import os
import sys
from collections import deque
from collections.abc import Iterator
from concurrent.futures import Future, ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from contextlib import contextmanager
from multiprocessing.synchronize import Barrier
from threading import BrokenBarrierError, Event
from time import perf_counter
from typing import TypeVar

from .errors import LabError, check_cancelled, check_range
from .notes import NoteSummary, NotesConfig, iter_batches, process_batch

T = TypeVar("T")
_startup_barrier: Barrier


class ProcessError(LabError):
    pass


def max_workers() -> int:
    cpu_count = getattr(os, "process_cpu_count", os.cpu_count)() or 1
    if hasattr(os, "sched_getaffinity"):
        cpu_count = min(cpu_count, len(os.sched_getaffinity(0)))
    return min(cpu_count, 61) if sys.platform == "win32" else cpu_count


def default_workers() -> int:
    return min(4, max_workers())

# Проверяем запрошенное число процессов и ограничиваем его количеством пакетов, чтобы не создавать лишние процессы.
def workers_for(config: NotesConfig, workers: int) -> int:
    check_range(workers, 1, max_workers(), "Количество процессов")
    return min(workers, config.batch_count)


def _init_worker(barrier: Barrier) -> None:
    global _startup_barrier
    _startup_barrier = barrier


def _worker_ready() -> None:
    _startup_barrier.wait(timeout=30)

# Ожидаем результат Future короткими интервалами по 0,05 с.
# Между попытками проверяем запрос пользователя на отмену.
def _await(future: Future[T], cancel: Event | None) -> T:
    while True:
        check_cancelled(cancel)
        try:
            return future.result(timeout=0.05)
        except TimeoutError:
            if future.done():
                return future.result()


# Создаём пул отдельных процессов через spawn.
# Barrier позволяет дождаться запуска всех рабочих процессов.
# После выхода из with пул корректно завершается.
@contextmanager
def note_pool(workers: int, cancel: Event | None = None) -> Iterator[tuple[ProcessPoolExecutor, float]]:
    check_cancelled(cancel)
    started = perf_counter()
    try:
        ctx = mp.get_context("spawn")
        barrier = ctx.Barrier(workers)
        executor = ProcessPoolExecutor(
            max_workers=workers, mp_context=ctx, initializer=_init_worker, initargs=(barrier,)
        )
        try:
            # Задача готовности занимает процесс, пока все процессы не запустятся.
            ready = [executor.submit(_worker_ready) for _ in range(workers)]
            for future in ready:
                _await(future, cancel)
            yield executor, perf_counter() - started
        finally:
            barrier.abort()
            executor.shutdown(wait=True, cancel_futures=True)
    except (OSError, BrokenProcessPool, BrokenBarrierError) as exc:
        detail = str(exc) or type(exc).__name__
        raise ProcessError(
            f"Ошибка пула процессов. Уменьшите число процессов и запустите операцию снова. {detail}"
        ) from exc


# Распределяем пакеты между процессами через ProcessPoolExecutor.
# Поддерживаем ограниченную очередь Future и возвращаем результаты в исходном порядке пакетов,
# независимо от порядка их завершения.
def parallel_batches(
    config: NotesConfig, executor: ProcessPoolExecutor, workers: int, cancel: Event | None = None
) -> Iterator[tuple[NoteSummary, int]]:
    pending: deque[Future[tuple[NoteSummary, int]]] = deque()
    batches = iter_batches(config)
    try:

        # Первоначально отправляем до 2 * workers заданий.
        # Одновременно выполняться могут не более workers заданий, остальные ожидают свободный процесс.
        for _ in range(2 * workers):
            check_cancelled(cancel)
            batch = next(batches, None)
            if batch is None:
                break
            pending.append(executor.submit(process_batch, batch))

        # Получаем результат первого Future в очереди.
        # Затем удаляем его и отправляем следующий пакет, поддерживая очередь до 2 * workers заданий.
        while pending:
            yield _await(pending[0], cancel)
            pending.popleft()
            check_cancelled(cancel)
            batch = next(batches, None)
            if batch is not None:
                pending.append(executor.submit(process_batch, batch))

    # При завершении или отмене пытаемся отменить задания, результаты которых ещё не были получены.
    finally:
        for future in pending:
            future.cancel()
