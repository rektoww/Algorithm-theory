
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


def get_connection():
    project_dir = Path(__file__).resolve().parents[2]
    load_dotenv(project_dir / ".env")

    password = os.getenv("SLEEPTRACKER_DB_PASSWORD")

    if not password:
        raise RuntimeError(
            "Не задан пароль SLEEPTRACKER_DB_PASSWORD"
        )

    return psycopg.connect(
        host="127.0.0.1",
        port=5433,
        dbname=os.getenv("SLEEPTRACKER_DB_NAME", "sleeptracker"),
        user="sleeptracker",
        password=password
    )


if __name__ == "__main__":
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), current_user;"
            )

            print(cursor.fetchone())
