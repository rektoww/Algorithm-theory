import pytest

from lab04.core.benchmark import BenchmarkResult, Measurements, compare
from lab04.core.errors import InputError
from lab04.core.generation import Mode
from lab04.core.notes import NotesConfig
from lab04.core.parallel import max_workers


@pytest.mark.parametrize("parallel_time,expected_speedup,expected_saved", [(2.0, 2.0, 50.0), (8.0, 0.5, -100.0)])
def test_medians_and_speedup_formula(parallel_time, expected_speedup, expected_saved):
    sequential = Measurements(Mode.SEQUENTIAL, (5.0, 3.0, 4.0), 1)
    parallel = Measurements(Mode.PARALLEL, (parallel_time * 2, parallel_time, parallel_time / 2), 2)
    result = BenchmarkResult(sequential, parallel, 10.0, 2, 42)
    assert sequential.median_seconds == 4.0
    assert result.speedup == expected_speedup
    assert result.time_saved_percent == expected_saved
    assert ("сократил" if expected_saved > 0 else "больше времени") in result.explanation


def test_real_timing_and_progress_excludes_warmup_from_samples():
    progress = []
    config = NotesConfig(count=517, batch_size=128, seed=-10, rounds=2)
    result = compare(config, min(2, max_workers()), repeats=2, progress=lambda done, total: progress.append((done, total)))
    assert result.seed == -10
    assert result.pool_setup_seconds > 0
    assert progress[-1] == (6 * config.count,) * 2
    assert [done for done, _ in progress] == sorted({done for done, _ in progress})
    for run in (result.sequential, result.parallel):
        assert len(run.samples) == 2
        assert all(seconds > 0 for seconds in run.samples)


@pytest.mark.parametrize("mode", list(Mode))
def test_single_mode(mode):
    result = compare(NotesConfig(count=129, batch_size=64), workers=1, repeats=1, mode=mode)
    selected, other = (result.sequential, result.parallel) if mode is Mode.SEQUENTIAL else (result.parallel, result.sequential)
    assert selected.mode is mode
    assert other is None
    assert result.speedup is None


def test_bad_repeat_count():
    with pytest.raises(InputError, match="Количество повторов"):
        compare(NotesConfig(), workers=1, repeats=0)


@pytest.mark.benchmark
@pytest.mark.parametrize("count,rounds", [(1_000_000, 0), (100_000, 32)])
def test_large_benchmark_runs(count, rounds):
    result = compare(NotesConfig(count=count, seed=42, rounds=rounds), min(2, max_workers()), repeats=2)
    assert result.speedup > 0
