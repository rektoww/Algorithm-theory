
import httpx
from PyQt6.QtCore import QDateTime
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMessageBox,
    QTableWidgetItem,
)


class RecordsController:
    def __init__(self, window, api):
        self.window = window
        self.api = api
        self.editing_record_id = None

        table = self.window.recordsTable

        table.setHorizontalHeaderLabels([
            "ID",
            "Засыпание",
            "Пробуждение",
            "Продолжительность",
            "Качество",
            "Комментарий",
        ])

        header = table.horizontalHeader()

        header.setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            5,
            QHeaderView.ResizeMode.Stretch
        )

        table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.window.refreshButton.clicked.connect(
            self.load_records
        )
        self.window.addButton.clicked.connect(
            self.save_record
        )
        self.window.editButton.clicked.connect(
            self.start_editing
        )
        self.window.cancelButton.clicked.connect(
            self.reset_form
        )
        self.window.deleteButton.clicked.connect(
            self.delete_record
        )

        self.reset_form()

    def load_records(self):
        try:
            records = self.api.get_records()

        except httpx.HTTPError as err:
            QMessageBox.warning(
                self.window,
                "Ошибка подключения",
                f"Не удалось получить записи:\n{err}"
            )
            return

        table = self.window.recordsTable
        table.setRowCount(len(records))

        for row, record in enumerate(records):
            minutes = record["duration_minutes"]
            duration = f"{minutes // 60} ч {minutes % 60} мин"

            values = [
                record["record_id"],
                record["fell_asleep_at"][:16].replace("T", " "),
                record["woke_up_at"][:16].replace("T", " "),
                duration,
                f'{record["quality"]}/5',
                record["notes"],
            ]

            for column, value in enumerate(values):
                table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value))
                )

    def reset_form(self):
        self.editing_record_id = None

        now = QDateTime.currentDateTime()

        self.window.wokeUpEdit.setDateTime(now)
        self.window.fellAsleepEdit.setDateTime(
            now.addSecs(-8 * 60 * 60)
        )

        self.window.qualitySpinBox.setValue(4)
        self.window.notesEdit.clear()

        self.window.addButton.setText("Добавить запись")
        self.window.cancelButton.setEnabled(False)

    def _selected_record_id(self):
        selected_rows = (
            self.window.recordsTable
            .selectionModel()
            .selectedRows()
        )

        if not selected_rows:
            return None

        row = selected_rows[0].row()
        item = self.window.recordsTable.item(row, 0)

        return int(item.text()) if item is not None else None

    def start_editing(self):
        record_id = self._selected_record_id()

        if record_id is None:
            QMessageBox.warning(
                self.window,
                "Запись не выбрана",
                "Выберите запись для редактирования"
            )
            return

        try:
            record = self.api.get_record(record_id)

        except httpx.HTTPError as err:
            QMessageBox.warning(
                self.window,
                "Ошибка загрузки",
                f"Не удалось получить запись:\n{err}"
            )
            return

        asleep = QDateTime.fromString(
            record["fell_asleep_at"][:19],
            "yyyy-MM-ddTHH:mm:ss"
        )

        wake_up = QDateTime.fromString(
            record["woke_up_at"][:19],
            "yyyy-MM-ddTHH:mm:ss"
        )

        if not asleep.isValid() or not wake_up.isValid():
            QMessageBox.warning(
                self.window,
                "Ошибка",
                "Не удалось прочитать даты записи"
            )
            return

        self.window.fellAsleepEdit.setDateTime(asleep)
        self.window.wokeUpEdit.setDateTime(wake_up)
        self.window.qualitySpinBox.setValue(record["quality"])
        self.window.notesEdit.setText(record["notes"])

        self.editing_record_id = record_id

        self.window.addButton.setText("Сохранить изменения")
        self.window.cancelButton.setEnabled(True)

    def save_record(self):
        asleep = (
            self.window.fellAsleepEdit
            .dateTime()
            .toPyDateTime()
        )

        wake_up = (
            self.window.wokeUpEdit
            .dateTime()
            .toPyDateTime()
        )

        if wake_up <= asleep:
            QMessageBox.warning(
                self.window,
                "Некорректное время",
                "Пробуждение должно быть позже засыпания"
            )
            return

        data = {
            "fell_asleep_at": asleep.isoformat(),
            "woke_up_at": wake_up.isoformat(),
            "quality": self.window.qualitySpinBox.value(),
            "notes": self.window.notesEdit.text().strip(),
        }

        try:
            if self.editing_record_id is None:
                self.api.create_record(data)
                message = "Запись о сне добавлена!"
            else:
                self.api.update_record(
                    self.editing_record_id,
                    data
                )
                message = "Изменения успешно сохранены!"

        except httpx.HTTPError as err:
            QMessageBox.warning(
                self.window,
                "Ошибка сохранения",
                f"Не удалось сохранить запись:\n{err}"
            )
            return

        self.reset_form()
        self.load_records()

        QMessageBox.information(
            self.window,
            "Успешно",
            message
        )

    def delete_record(self):
        record_id = self._selected_record_id()

        if record_id is None:
            QMessageBox.warning(
                self.window,
                "Запись не выбрана",
                "Сначала выберите запись в таблице"
            )
            return

        answer = QMessageBox.question(
            self.window,
            "Подтверждение удаления",
            f"Удалить запись №{record_id}?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            self.api.delete_record(record_id)

        except httpx.HTTPError as err:
            QMessageBox.warning(
                self.window,
                "Ошибка удаления",
                f"Не удалось удалить запись:\n{err}"
            )
            return

        if self.editing_record_id == record_id:
            self.reset_form()

        self.load_records()

        QMessageBox.information(
            self.window,
            "Успешно",
            "Запись успешно удалена"
        )
