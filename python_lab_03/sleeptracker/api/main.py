
from fastapi import FastAPI, HTTPException


from sleeptracker.api.schemas import (
    SleepRecordCreate,
    SleepRecordResponse,
)

from sleeptracker.domain.sleep_statistics import SleepStatistics
from sleeptracker.domain.sleep_record import SleepRecord
from sleeptracker.database.sleep_repository import SleepRepository
from sleeptracker.database.activity_log_repository import ActivityLogRepository
from sleeptracker.api.schemas import ActivityLogResponse

app = FastAPI(
    title="SleepTracker API",
    description="API приложения для отслеживания сна",
    version="1.0.0"
)

repository = SleepRepository()
activity_repository = ActivityLogRepository()

@app.get("/")
def root():
    return {"message": "SleepTracker API работает"}


@app.get("/records", response_model=list[SleepRecordResponse])
def get_records():
    return repository.get_all()


@app.post(
    "/records",
    response_model=SleepRecordResponse,
    status_code=201
)
def create_record(data: SleepRecordCreate):
    record = SleepRecord(**data.model_dump())

    record_id = repository.add(record)

    return repository.get_by_id(record_id)

@app.get("/records/{record_id}", response_model=SleepRecordResponse)
def get_record(record_id: int):
    record = repository.get_by_id(record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Запись о сне не найдена"
        )

    return record

@app.put("/records/{record_id}", response_model=SleepRecordResponse)
def update_record(record_id: int, data: SleepRecordCreate):
    record = SleepRecord(
        **data.model_dump(),
        record_id=record_id
    )

    if not repository.update(record):
        raise HTTPException(
            status_code=404,
            detail="Запись о сне не найдена"
        )

    return repository.get_by_id(record_id)

@app.delete("/records/{record_id}", status_code=204)
def delete_record(record_id: int):
    if not repository.delete(record_id):
        raise HTTPException(
            status_code=404,
            detail="Запись о сне не найдена"
        )


@app.get("/statistics")
def get_statistics():
    records = repository.get_all()
    statistics = SleepStatistics(records)

    return {
        "record_count": statistics.record_count,
        "average_duration_minutes": statistics.average_duration_minutes,
        "shortest_duration_minutes": statistics.shortest_duration_minutes,
        "longest_duration_minutes": statistics.longest_duration_minutes,
        "duration_by_day": [
            {
                "date": day.isoformat(),
                "duration_minutes": minutes
            }
            for day, minutes in statistics.duration_by_day.items()
        ]
    }


@app.get("/activity-log", response_model=list[ActivityLogResponse])
def get_activity_log():
    return activity_repository.get_all()
