
import pytest

from fastapi.testclient import TestClient

from sleeptracker.api.main import app
from sleeptracker.database.connection import get_connection


def test_root():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "SleepTracker API работает"
    }


def test_not_found():
    with TestClient(app) as client:
        response = client.get("/unknown")

    assert response.status_code == 404


@pytest.fixture
def api_client(monkeypatch):
    monkeypatch.setenv(
        "SLEEPTRACKER_DB_NAME",
        "sleeptracker_test"
    )

    def clear_test_database():
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database();")
                database_name = cursor.fetchone()[0]

                if database_name != "sleeptracker_test":
                    raise RuntimeError(
                        "Очистка основной базы запрещена!"
                    )

                cursor.execute("""
                    TRUNCATE TABLE activity_logs, sleep_records
                    RESTART IDENTITY;
                """)

    clear_test_database()

    try:
        with TestClient(app) as client:
            yield client
    finally:
        clear_test_database()


def test_api_crud_and_activity_log(api_client):
    data = {
        "fell_asleep_at": "2026-11-01T23:00:00",
        "woke_up_at": "2026-11-02T07:00:00",
        "quality": 4,
        "notes": "Тестовая запись"
    }

    # Создание
    response = api_client.post("/records", json=data)

    assert response.status_code == 201

    record_id = response.json()["record_id"]
    assert response.json()["duration_minutes"] == 480

    # Получение одной записи
    response = api_client.get(f"/records/{record_id}")

    assert response.status_code == 200
    assert response.json()["quality"] == 4

    # Получение списка
    response = api_client.get("/records")

    assert response.status_code == 200
    assert len(response.json()) == 1

    # Редактирование
    updated_data = {
        **data,
        "woke_up_at": "2026-11-02T08:00:00",
        "quality": 5
    }

    response = api_client.put(
        f"/records/{record_id}",
        json=updated_data
    )

    assert response.status_code == 200
    assert response.json()["quality"] == 5
    assert response.json()["duration_minutes"] == 540

    # Удаление
    response = api_client.delete(f"/records/{record_id}")

    assert response.status_code == 204
    assert api_client.get(f"/records/{record_id}").status_code == 404

    # Проверка журнала
    response = api_client.get("/activity-log")

    assert response.status_code == 200

    events = response.json()

    assert len(events) == 3
    assert [event["action"] for event in reversed(events)] == [
        "created",
        "updated",
        "deleted"
    ]
    assert all(
        event["record_id"] == record_id
        for event in events
    )


@pytest.mark.parametrize("quality", [0, 6])
def test_api_invalid_quality(api_client, quality):
    data = {
        "fell_asleep_at": "2026-11-01T23:00:00",
        "woke_up_at": "2026-11-02T07:00:00",
        "quality": quality
    }

    response = api_client.post("/records", json=data)

    assert response.status_code == 422
    assert api_client.get("/records").json() == []


def test_api_invalid_sleep_time(api_client):
    data = {
        "fell_asleep_at": "2026-11-01T23:00:00",
        "woke_up_at": "2026-11-01T22:00:00",
        "quality": 4
    }

    response = api_client.post("/records", json=data)

    assert response.status_code == 422
    assert api_client.get("/records").json() == []


def test_api_missing_record(api_client):
    record_id = 999999

    response = api_client.get(f"/records/{record_id}")
    assert response.status_code == 404

    data = {
        "fell_asleep_at": "2026-11-01T23:00:00",
        "woke_up_at": "2026-11-02T07:00:00",
        "quality": 4
    }

    response = api_client.put(
        f"/records/{record_id}",
        json=data
    )
    assert response.status_code == 404

    response = api_client.delete(f"/records/{record_id}")
    assert response.status_code == 404


def test_api_empty_statistics(api_client):
    response = api_client.get("/statistics")

    assert response.status_code == 200

    statistics = response.json()

    assert statistics["record_count"] == 0
    assert statistics["average_duration_minutes"] == 0.0
    assert statistics["shortest_duration_minutes"] is None
    assert statistics["longest_duration_minutes"] is None
    assert statistics["duration_by_day"] == []


def test_api_statistics(api_client):
    records = [
        {
            "fell_asleep_at": "2026-11-01T23:00:00",
            "woke_up_at": "2026-11-02T07:00:00",
            "quality": 4
        },
        {
            "fell_asleep_at": "2026-11-02T14:00:00",
            "woke_up_at": "2026-11-02T15:00:00",
            "quality": 3
        },
        {
            "fell_asleep_at": "2026-11-02T23:00:00",
            "woke_up_at": "2026-11-03T08:00:00",
            "quality": 5
        }
    ]

    for record in records:
        response = api_client.post("/records", json=record)
        assert response.status_code == 201

    response = api_client.get("/statistics")

    assert response.status_code == 200

    statistics = response.json()

    assert statistics["record_count"] == 3
    assert statistics["average_duration_minutes"] == 360
    assert statistics["shortest_duration_minutes"] == 60
    assert statistics["longest_duration_minutes"] == 540

    assert statistics["duration_by_day"] == [
        {
            "date": "2026-11-02",
            "duration_minutes": 540
        },
        {
            "date": "2026-11-03",
            "duration_minutes": 540
        }
    ]
