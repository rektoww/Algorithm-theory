
from .connection import get_connection


def create_tables():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sleep_records (
                    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    fell_asleep_at TIMESTAMP NOT NULL,
                    woke_up_at TIMESTAMP NOT NULL,
                    quality INTEGER NOT NULL CHECK (quality BETWEEN 1 AND 5),
                    notes TEXT NOT NULL DEFAULT '',

                    CHECK (woke_up_at > fell_asleep_at)
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    record_id BIGINT NOT NULL,
                    action VARCHAR(10) NOT NULL
                        CHECK (action IN ('created', 'updated', 'deleted')),
                    details TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)

    print("Таблицы базы данных успешно созданы")


if __name__ == "__main__":
    create_tables()
