from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


# basemodel - Базовый класс моделей pydantic
class SleepRecordCreate(BaseModel):
    fell_asleep_at: datetime
    woke_up_at: datetime
    quality: int = Field(ge=1, le=5)
    notes: str = ""

    @model_validator(mode="after")
    def validate_sleep_time(self):
        if self.woke_up_at <= self.fell_asleep_at:
            raise ValueError(
                "Время пробуждения должно быть позже засыпания"
            )

        return self


class SleepRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    record_id: int
    fell_asleep_at: datetime
    woke_up_at: datetime
    quality: int
    notes: str
    duration_minutes: int

class ActivityLogResponse(BaseModel):
    id: int
    record_id: int
    action: str
    details: str
    created_at: datetime
