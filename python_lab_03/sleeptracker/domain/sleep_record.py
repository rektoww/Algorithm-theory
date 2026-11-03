from dataclasses import dataclass
from datetime import datetime

from .exceptions import InvalidSleepQualityError, InvalidSleepTimeError

@dataclass
class SleepRecord:
    fell_asleep_at: datetime
    woke_up_at: datetime
    quality: int
    notes: str = ""
    record_id: int | None = None

    def __post_init__(self):
        if self.woke_up_at <= self.fell_asleep_at:
            raise InvalidSleepTimeError(
                "Время пробуждения должно быть позже времени засыпания"
            )

        if not 1 <= self.quality <= 5:
            raise InvalidSleepQualityError(
                "Качество сна должно быть от 1 до 5"
            )

    @property
    def duration_minutes(self):
        duration = self.woke_up_at - self.fell_asleep_at
        return int(duration.total_seconds() // 60)
