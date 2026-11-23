from multiprocessing import active_children
from os import getpid
from threading import Event

import pytest

from lab04.core.errors import Cancelled, InputError
from lab04.core.generation import Mode, run_notes
from lab04.core.notes import NotesConfig
from lab04.core.parallel import ProcessError, max_workers


@pytest.mark.parametrize("count,size,rounds", [(503, 7, 0), (323, 32, 0), (13, 50, 0), (1041, 256, 3)])
def test_parallel_matches_sequential(count, size, rounds):
    workers = min(2, max_workers())
    config = NotesConfig(count=count, seed=13, batch_size=size, rounds=rounds)
    sequential = run_notes(config, Mode.SEQUENTIAL)
    parallel = run_notes(config, Mode.PARALLEL, workers)
    assert parallel.result.summary == sequential.result.summary
    assert parallel.result.summary.count == count
    assert sum(parallel.result.summary.frequencies) == count
    assert len(parallel.result.summary.preview) == min(20, count)
    assert getpid() not in parallel.result.process_ids
    assert parallel.pool_workers == min(workers, config.batch_count)
    assert len(parallel.result.process_ids) <= parallel.pool_workers
    assert not parallel.result.process_ids.intersection(child.pid for child in active_children())


@pytest.mark.skipif(max_workers() < 2, reason="Требуются два доступных процесса")
def test_uses_multiple_processes_for_cpu_work():
    config = NotesConfig(count=24000, seed=7, batch_size=3000, rounds=24)
    output = run_notes(config, Mode.PARALLEL, workers=2)
    assert len(output.result.process_ids) == 2


@pytest.mark.parametrize("workers", [0, -1, max_workers() + 1])
def test_bad_worker_counts(workers):
    with pytest.raises(InputError, match="Количество процессов"):
        run_notes(NotesConfig(count=23), Mode.PARALLEL, workers)


def test_process_start_failure_is_reported(monkeypatch):
    def fail(**options):
        raise OSError("test error")

    monkeypatch.setattr("lab04.core.parallel.ProcessPoolExecutor", fail)
    with pytest.raises(ProcessError, match="Ошибка пула процессов.*test error"):
        run_notes(NotesConfig(count=23), Mode.PARALLEL, workers=1)


@pytest.mark.parametrize("mode", list(Mode))
def test_cancel_after_first_batch(mode):
    cancel = Event()
    children = {child.pid for child in active_children()}
    seen = []

    def interrupt(count, total):
        seen.append((count, total))
        cancel.set()

    with pytest.raises(Cancelled, match="остановлена"):
        run_notes(NotesConfig(count=10_100, seed=42, batch_size=100), mode, cancel=cancel, progress=interrupt)
    assert seen == [(100, 10_100)]
    assert {child.pid for child in active_children()} <= children
