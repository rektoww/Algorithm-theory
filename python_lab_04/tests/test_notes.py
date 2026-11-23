from collections import Counter
from itertools import chain, islice
from random import Random
from types import GeneratorType

import pytest

from lab04.core.errors import InputError
from lab04.core.generation import Mode, run_notes
from lab04.core.notes import DEFAULT_COUNT, NOTES, NotesConfig, iter_batches, random_notes


def test_random_notes_are_lazy_and_default_to_one_million():
    generator = random_notes(seed=42)
    assert DEFAULT_COUNT == 1_000_000
    assert isinstance(generator, GeneratorType)
    rng = Random(42)
    assert list(islice(generator, 20)) == [rng.choice(NOTES) for _ in range(20)]


def test_random_notes_count_members_and_repeatability():
    result = list(random_notes(120, seed=-9))
    assert len(result) == 120
    assert set(result) == set(NOTES)
    assert list(random_notes(120, seed=-9)) == result


@pytest.mark.parametrize("count", [0, -1, 2.5, True])
def test_invalid_count(count):
    with pytest.raises(InputError, match="Количество нот"):
        next(random_notes(count))
    with pytest.raises(InputError, match="Количество нот"):
        NotesConfig(count=count)


@pytest.mark.parametrize("options", [{"seed": "42"}, {"rounds": -1}, {"rounds": 257}, {"batch_size": 0}])
def test_invalid_options(options):
    with pytest.raises(InputError):
        NotesConfig(**options)


@pytest.mark.parametrize("count,size,expected", [(9, 4, [4, 4, 1]), (8, 4, [4, 4]), (7, 10, [7]), (3, 1, [1, 1, 1])])
def test_batches(count, size, expected):
    configs = NotesConfig(count=count, batch_size=size, seed=23)
    batches = tuple(iter_batches(configs))
    assert [batch.count for batch in batches] == expected
    assert len(batches) == configs.batch_count
    assert len({batch.seed for batch in batches}) == len(batches)
    assert tuple(iter_batches(configs)) == batches


def test_sequential_summary_matches_reference_stream():
    config = NotesConfig(count=317, batch_size=8, seed=42)
    raw = list(chain.from_iterable(random_notes(batch.count, batch.seed) for batch in iter_batches(config)))
    expected = Counter(raw)
    output = run_notes(config, Mode.SEQUENTIAL)
    assert output.result.summary.count == len(raw)
    assert output.result.summary.preview == tuple(raw[:20])
    assert output.result.summary.frequencies == tuple(expected[note] for note in NOTES)
    assert len(output.result.process_ids) == 1
    assert output.seed == 42
    assert output.seconds > 0


def test_automatic_seed_can_be_replayed():
    selected = run_notes(NotesConfig(count=30), Mode.SEQUENTIAL)
    replay = run_notes(NotesConfig(count=30, seed=selected.seed), Mode.SEQUENTIAL)
    assert replay.result.summary == selected.result.summary
