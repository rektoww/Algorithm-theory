from itertools import islice

from PyQt6.QtWidgets import (
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)

from ..core.emails import DEMO_EMAILS, check_emails
from ..core.errors import InputError, parse_integer
from ..core.multiples import multiples_of_three
from .widgets import spin, wrapped_label


class MultiplesTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        description = wrapped_label(
            "Функция находит первое кратное трём число, начиная с a включительно. yield выдаёт значения по одному с шагом 3."
        )
        description.setObjectName("muted")
        layout.addWidget(description)
        settings = QGroupBox("Параметры")
        form = QFormLayout(settings)
        self.start = QLineEdit("-100")
        self.count = spin(1, 10_000, 20)
        form.addRow("Начальное значение a", self.start)
        form.addRow("Количество чисел", self.count)
        self.generate = QPushButton("Показать числа")
        self.generate.setObjectName("primary")
        form.addRow(self.generate)
        layout.addWidget(settings)
        self.status = wrapped_label()
        layout.addWidget(self.status)
        results = QGroupBox("Числа, кратные 3")
        output = QVBoxLayout(results)
        self.values = QPlainTextEdit()
        self.values.setReadOnly(True)
        output.addWidget(self.values)
        layout.addWidget(results, 1)
        self.generate.clicked.connect(self.show_multiples)
        self.start.returnPressed.connect(self.show_multiples)
        self.show_multiples()

    def show_multiples(self) -> None:
        try:
            start = parse_integer(self.start.text(), "Начальное значение a")
            values = islice(multiples_of_three(start), self.count.value())
            text = "  ·  ".join(map(str, values))
        except (InputError, ValueError) as exc:
            self.values.clear()
            self.status.setText(str(exc) if isinstance(exc, InputError) else "Уменьшите начальное значение a по модулю.")
            return
        self.values.setPlainText(text)
        self.status.setText(f"Показано чисел — {self.count.value()}")


class EmailsTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        description = wrapped_label(
            "Введите адреса через пробел. Допустимы буквы A–Z и a–z, цифры и _. После @ нужны две или более непустых части домена через точку."
        )
        description.setObjectName("muted")
        layout.addWidget(description)
        source = QGroupBox("Исходные адреса")
        source_layout = QVBoxLayout(source)
        self.addresses = QLineEdit()
        self.addresses.setPlaceholderText("name@site.ru user_2@dept.site.ru")
        source_layout.addWidget(self.addresses)
        buttons = QHBoxLayout()
        self.check = QPushButton("Проверить")
        self.check.setObjectName("primary")
        self.example = QPushButton("Пример данных")
        buttons.addWidget(self.check)
        buttons.addWidget(self.example)
        buttons.addStretch(1)
        source_layout.addLayout(buttons)
        layout.addWidget(source)

        self.status = QLabel()
        layout.addWidget(self.status)
        columns = QHBoxLayout()
        accepted_box = QGroupBox("Корректные адреса")
        accepted_layout = QVBoxLayout(accepted_box)
        self.accepted = QPlainTextEdit()
        self.accepted.setReadOnly(True)
        accepted_layout.addWidget(self.accepted)
        rejected_box = QGroupBox("Отклонённые адреса")
        rejected_layout = QVBoxLayout(rejected_box)
        self.rejected = QPlainTextEdit()
        self.rejected.setReadOnly(True)
        rejected_layout.addWidget(self.rejected)
        columns.addWidget(accepted_box, 2)
        columns.addWidget(rejected_box, 3)
        layout.addLayout(columns, 1)
        self.check.clicked.connect(self.show_emails)
        self.example.clicked.connect(self.load_example)
        self.addresses.returnPressed.connect(self.show_emails)

    def load_example(self) -> None:
        self.addresses.setText(DEMO_EMAILS)
        self.addresses.setCursorPosition(0)

    def show_emails(self) -> None:
        try:
            result = check_emails(self.addresses.text())
        except InputError as exc:
            self.status.setText(str(exc))
            self.accepted.clear()
            self.rejected.clear()
            return
        self.accepted.setPlainText("\n".join(result.accepted))
        self.rejected.setPlainText("\n\n".join(f"{item.address}\n{item.reason}" for item in result.rejected))
        self.status.setText(
            f"Проверено {len(result.addresses)}    ·    Корректных {len(result.accepted)}    ·    Отклонено {len(result.rejected)}"
        )
