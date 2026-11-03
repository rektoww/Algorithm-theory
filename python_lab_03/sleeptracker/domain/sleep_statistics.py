from .sleep_record import SleepRecord
from datetime import date


class SleepStatistics:
    def __init__(self, records: list[SleepRecord]):
        self._records = list(records)

    @property
    def record_count(self) -> int:
        return len(self._records)

    @property
    def average_duration_minutes(self) -> float:
        if not self._records:
            return 0.0

        total = sum(
            record.duration_minutes
            for record in self._records
        )

        return total / self.record_count

    @property
    def shortest_duration_minutes(self) -> int | None:
        return min(
            (record.duration_minutes for record in self._records),
            default=None
        )

    @property
    def longest_duration_minutes(self) -> int | None:
        return max(
            (record.duration_minutes for record in self._records),
            default=None
        )


    @property
    def duration_by_day(self) -> dict[date, int]:
        result = {}

        for record in self._records:
            day = record.woke_up_at.date()

            result[day] = (
                result.get(day, 0)
                + record.duration_minutes
            )

        return dict(sorted(result.items()))
