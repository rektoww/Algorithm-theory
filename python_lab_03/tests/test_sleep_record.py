
from datetime import datetime

import pytest

from sleeptracker.domain.sleep_record import SleepRecord
from sleeptracker.domain.exceptions import (
    InvalidSleepTimeError,
    InvalidSleepQualityError,
)


def test_duration_across_midnight():
    record = SleepRecord(
        datetime(2026, 10, 30, 23, 30),
        datetime(2026, 10, 31, 7, 15),
        quality=4
    )

    assert record.duration_minutes == 465


def test_duration_same_day():
    record = SleepRecord(
        datetime(2026, 10, 31, 1, 0),
        datetime(2026, 10, 31, 8, 30),
        quality=5
    )

    assert record.duration_minutes == 450


@pytest.mark.parametrize("woke_up_at", [
    datetime(2026, 10, 31, 23, 30),
    datetime(2026, 10, 31, 22, 30)
])
def test_invalid_sleep_time(woke_up_at):
    with pytest.raises(InvalidSleepTimeError):
        SleepRecord(
            datetime(2026, 10, 31, 23, 30),
            woke_up_at,
            quality=3
        )


@pytest.mark.parametrize("quality", [0, 6])
def test_invalid_sleep_quality(quality):
    with pytest.raises(InvalidSleepQualityError):
        SleepRecord(
            datetime(2026, 10, 30, 23, 0),
            datetime(2026, 10, 31, 7, 0),
            quality=quality
        )


def test_default_values():
    record = SleepRecord(
        datetime(2026, 10, 30, 23, 0),
        datetime(2026, 10, 31, 7, 0),
        quality=4
    )

    assert record.notes == ""
    assert record.record_id is None
