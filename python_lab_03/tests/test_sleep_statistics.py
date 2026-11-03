
from datetime import datetime
from datetime import date

from sleeptracker.domain.sleep_record import SleepRecord
from sleeptracker.domain.sleep_statistics import SleepStatistics


def test_sleep_statistics():
    records = [
        SleepRecord(
            datetime(2026, 10, 28, 22, 0),
            datetime(2026, 10, 29, 6, 0),
            quality=4
        ),
        SleepRecord(
            datetime(2026, 10, 29, 23, 0),
            datetime(2026, 10, 30, 6, 0),
            quality=3
        ),
        SleepRecord(
            datetime(2026, 10, 30, 23, 0),
            datetime(2026, 10, 31, 8, 0),
            quality=5
        )
    ]

    statistics = SleepStatistics(records)

    assert statistics.record_count == 3
    assert statistics.average_duration_minutes == 480
    assert statistics.shortest_duration_minutes == 420
    assert statistics.longest_duration_minutes == 540


def test_empty_sleep_statistics():
    statistics = SleepStatistics([])

    assert statistics.record_count == 0
    assert statistics.average_duration_minutes == 0.0
    assert statistics.shortest_duration_minutes is None
    assert statistics.longest_duration_minutes is None


def test_duration_by_day():
    records = [
        SleepRecord(
            datetime(2026, 10, 29, 23, 0),
            datetime(2026, 10, 30, 7, 0),
            quality=4
        ),
        SleepRecord(
            datetime(2026, 10, 30, 14, 0),
            datetime(2026, 10, 30, 15, 0),
            quality=3
        ),
        SleepRecord(
            datetime(2026, 10, 30, 23, 0),
            datetime(2026, 10, 31, 8, 0),
            quality=5
        )
    ]

    statistics = SleepStatistics(records)

    assert statistics.duration_by_day == {
        date(2026, 10, 30): 540,
        date(2026, 10, 31): 540
    }


def test_duration_by_day_empty():
    statistics = SleepStatistics([])

    assert statistics.duration_by_day == {}
