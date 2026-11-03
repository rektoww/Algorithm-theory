
from .connection import get_connection


class ActivityLogRepository:
    def get_all(self) -> list[dict]:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        id,
                        record_id,
                        action,
                        details,
                        created_at
                    FROM activity_logs
                    ORDER BY created_at DESC, id DESC;
                """)

                rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "record_id": row[1],
                "action": row[2],
                "details": row[3],
                "created_at": row[4]
            }
            for row in rows
        ]
