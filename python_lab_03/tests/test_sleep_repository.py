
from datetime import datetime

import pytest

from sleeptracker.domain.sleep_record import SleepRecord
from sleeptracker.database.connection import get_connection
from sleeptracker.database.sleep_repository import SleepRepository


@pytest.fixture
def repository(monkeypatch):
    monkeypatch.setenv(
        "SLEEPTRACKER_DB_NAME",
        "sleeptracker_test"
    )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            database_name = cursor.fetchone()[0]

            assert database_name == "sleeptracker_test"

            cursor.execute("""
                TRUNCATE TABLE activity_logs, sleep_records
                RESTART IDENTITY;
            """)

    yield SleepRepository()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                TRUNCATE TABLE activity_logs, sleep_records
                RESTART IDENTITY;
            """)


def test_repository_crud_and_activity_log(repository):
    record = SleepRecord(
        fell_asleep_at=datetime(2026, 10, 30, 23, 30),
        woke_up_at=datetime(2026, 10, 31, 7, 15),
        quality=4,
        notes="Хорошо выспался"
    )

    # Создание
    record_id = repository.add(record)
    assert isinstance(record_id, int)

    # Чтение
    saved = repository.get_by_id(record_id)
    assert saved is not None
    assert saved.quality == 4
    assert saved.duration_minutes == 465

    records = repository.get_all()
    assert len(records) == 1

    # Обновление
    updated = SleepRecord(
        fell_asleep_at=record.fell_asleep_at,
        woke_up_at=record.woke_up_at,
        quality=5,
        notes="Отлично выспался",
        record_id=record_id
    )

    assert repository.update(updated) is True
    assert repository.get_by_id(record_id).quality == 5

    # Удаление
    assert repository.delete(record_id) is True
    assert repository.get_by_id(record_id) is None
    assert repository.get_all() == []

    # Проверка журнала
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT record_id, action
                FROM activity_logs
                ORDER BY id;
            """)

            events = cursor.fetchall()

    assert events == [
        (record_id, "created"),
        (record_id, "updated"),
        (record_id, "deleted")
    ]
