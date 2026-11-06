
from datetime import datetime

import httpx

from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMessageBox,
    QTableWidgetItem,
)


class ActivityController:
    def __init__(self, window, api):
        self.window = window
        self.api = api

        table = self.window.activityTable

        table.setHorizontalHeaderLabels([
            "Дата и время",
            "Действие",
            "ID записи",
            "Описание",
        ])

        header = table.horizontalHeader()

        header.setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Stretch
        )

        table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.window.refreshActivityButton.clicked.connect(
            self.load_activity_log
        )

    def load_activity_log(self):
        try:
            events = self.api.get_activity_log()

        except httpx.HTTPError as err:
            QMessageBox.warning(
                self.window,
                "Ошибка загрузки",
                f"Не удалось получить историю:\n{err}"
            )
            return

        table = self.window.activityTable
        table.setRowCount(len(events))

        action_names = {
            "created": "Добавление",
            "updated": "Изменение",
            "deleted": "Удаление",
        }

        for row, event in enumerate(events):
            event_time = datetime.fromisoformat(
                event["created_at"]
            ).astimezone()

            values = [
                event_time.strftime("%d.%m.%Y %H:%M"),
                action_names.get(
                    event["action"],
                    event["action"]
                ),
                event["record_id"],
                event["details"],
            ]

            for column, value in enumerate(values):
                table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value))
                )
