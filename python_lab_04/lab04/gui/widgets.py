from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from ..core.errors import parse_integer


def spin(low: int, high: int, value: int) -> QSpinBox:
    field = QSpinBox()
    field.setRange(low, high)
    field.setValue(value)
    field.setGroupSeparatorShown(True)
    return field


def wrapped_label(text: str = "") -> QLabel:
    label = QLabel(text)
    label.setTextFormat(Qt.TextFormat.PlainText)
    label.setWordWrap(True)
    return label


def seed_field() -> QLineEdit:
    field = QLineEdit("42")
    field.setPlaceholderText("Случайное зерно")
    return field


def seed_value(field: QLineEdit) -> int | None:
    value = field.text().strip()
    return parse_integer(value, "Seed") if value else None


def grouped(value: int) -> str:
    return f"{value:,}".replace(",", "\u202f")


class RunControls(QWidget):
    requested = pyqtSignal()
    stop_requested = pyqtSignal()

    def __init__(self, button_text: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        buttons = QHBoxLayout()
        self.start = QPushButton(button_text)
        self.start.setObjectName("primary")
        self.stop = QPushButton("Остановить")
        self.stop.setEnabled(False)
        buttons.addWidget(self.start, 1)
        buttons.addWidget(self.stop)
        layout.addLayout(buttons)
        self.progress = QProgressBar()
        self.progress.setRange(0, 1000)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        self.status = wrapped_label("Готово к запуску.")
        self.status.setObjectName("muted")
        self.status.setMinimumHeight(34)
        layout.addWidget(self.status)
        self.start.clicked.connect(self.requested)
        self.stop.clicked.connect(self.stop_requested)

    def set_busy(self, busy: bool, active: bool) -> None:
        self.start.setEnabled(not busy)
        self.stop.setEnabled(active)
        if active:
            self.progress.setValue(0)
            self.status.setText("Подготовка к запуску…")

    # прогресс бар
    def update_progress(self, completed: int, total: int) -> None:
        self.progress.setValue(completed * 1000 // total)
        self.status.setText(f"Обработано {grouped(completed)} из {grouped(total)}")

    def stopping(self) -> None:
        self.stop.setEnabled(False)
        self.status.setText("Остановка. Завершаются пакеты в работе…")


class WorkTab(QWidget):
    def __init__(self, description: str, result_title: str, button_text: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        introduction = wrapped_label(description)
        introduction.setObjectName("muted")
        layout.addWidget(introduction)

        columns = QHBoxLayout()
        columns.setSpacing(16)
        layout.addLayout(columns, 1)
        settings = QGroupBox("Параметры")
        settings_layout = QVBoxLayout(settings)

        self._form_host = QWidget()
        self.form = QFormLayout(self._form_host)

        self.form.setContentsMargins(0, 0, 0, 0)
        self.form.setVerticalSpacing(7)

        self.controls = RunControls(button_text)

        settings_layout.addWidget(self._form_host)
        settings_layout.addStretch(1)
        settings_layout.addWidget(self.controls)

        result = QGroupBox(result_title)
        self.result = QVBoxLayout(result)
        self.result.setSpacing(12)
        columns.addWidget(settings, 3)
        columns.addWidget(result, 5)

    def set_busy(self, busy: bool, active: bool) -> None:
        self._form_host.setEnabled(not busy)
        self.controls.set_busy(busy, active)
