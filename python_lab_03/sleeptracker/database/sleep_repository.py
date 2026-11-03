
from sleeptracker.domain.sleep_record import SleepRecord
from .connection import get_connection


class SleepRepository:
    def add(self, record: SleepRecord) -> int:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO sleep_records (
                        fell_asleep_at,
                        woke_up_at,
                        quality,
                        notes
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """, (
                    record.fell_asleep_at,
                    record.woke_up_at,
                    record.quality,
                    record.notes
                ))

                record_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO activity_logs (
                        record_id,
                        action,
                        details
                    )
                    VALUES (%s, %s, %s);
                """, (
                    record_id,
                    "created",
                    "Добавлена запись о сне"
                ))

        return record_id

    @staticmethod
    def _row_to_record(row) -> SleepRecord:
        return SleepRecord(
            fell_asleep_at=row[1],
            woke_up_at=row[2],
            quality=row[3],
            notes=row[4],
            record_id=row[0]
        )

    def get_all(self) -> list[SleepRecord]:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        id,
                        fell_asleep_at,
                        woke_up_at,
                        quality,
                        notes
                    FROM sleep_records
                    ORDER BY woke_up_at DESC, id DESC;
                """)

                rows = cursor.fetchall()

        return [self._row_to_record(row) for row in rows]

    def get_by_id(self, record_id: int) -> SleepRecord | None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        id,
                        fell_asleep_at,
                        woke_up_at,
                        quality,
                        notes
                    FROM sleep_records
                    WHERE id = %s;
                """, (record_id,))

                row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_record(row)


    def update(self, record: SleepRecord) -> bool:
        if record.record_id is None:
            return False

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE sleep_records
                    SET
                        fell_asleep_at = %s,
                        woke_up_at = %s,
                        quality = %s,
                        notes = %s
                    WHERE id = %s
                    RETURNING id;
                """, (
                    record.fell_asleep_at,
                    record.woke_up_at,
                    record.quality,
                    record.notes,
                    record.record_id
                ))

                if cursor.fetchone() is None:
                    return False

                cursor.execute("""
                    INSERT INTO activity_logs (
                        record_id, action, details
                    )
                    VALUES (%s, %s, %s);
                """, (
                    record.record_id,
                    "updated",
                    "Изменена запись о сне"
                ))

        return True

    def delete(self, record_id: int) -> bool:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM sleep_records
                    WHERE id = %s
                    RETURNING id;
                """, (record_id,))

                if cursor.fetchone() is None:
                    return False

                cursor.execute("""
                    INSERT INTO activity_logs (
                        record_id, action, details
                    )
                    VALUES (%s, %s, %s);
                """, (
                    record_id,
                    "deleted",
                    "Удалена запись о сне"
                ))

        return True
