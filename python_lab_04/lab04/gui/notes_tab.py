from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QComboBox, QHeaderView, QLabel, QTableWidget, QTableWidgetItem

from ..core.errors import InputError
from ..core.generation import Mode, NoteRun
from ..core.notes import DEFAULT_COUNT, MAX_COUNT, NOTES, NotesConfig
from ..core.parallel import default_workers, max_workers
from .widgets import WorkTab, grouped, seed_field, seed_value, spin, wrapped_label


class NotesTab(WorkTab):
    requested = pyqtSignal(object, object, int)

    def __init__(self) -> None:
        super().__init__(
            "Генератор выбирает по одной ноте с помощью random.choice. В результатах сохраняются первые 20 нот и частоты.",
            "Результат генерации",
            "Сгенерировать",
        )
        self.mode = QComboBox()
        for mode in Mode:
            self.mode.addItem(mode.label, mode.value)
        self.count = spin(1, MAX_COUNT, DEFAULT_COUNT)
        self.seed = seed_field()
        self.workers = spin(1, max_workers(), default_workers())
        self.workers.setEnabled(False)
        self.mode.currentIndexChanged.connect(self._update_mode)
        self.form.addRow("Режим", self.mode)
        self.form.addRow("Количество нот", self.count)
        self.form.addRow("Seed", self.seed)
        self.form.addRow("Процессов в пуле", self.workers)
        self.controls.requested.connect(self._request)
        self.result.setSpacing(8)

        self.metrics = wrapped_label()
        self.metrics.setObjectName("metrics")
        self.metrics.hide()
        self.result.addWidget(self.metrics)
        self.result.addWidget(QLabel("Первые 20 нот"))
        self.preview = wrapped_label("Результат появится после генерации.")
        self.preview.setObjectName("preview")
        self.preview.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.result.addWidget(self.preview)

        self.table = QTableWidget(len(NOTES), 2)
        self.table.setHorizontalHeaderLabels(("Нота", "Частота"))
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(22)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setAlternatingRowColors(True)
        for row, note in enumerate(NOTES):
            self.table.setItem(row, 0, QTableWidgetItem(note))
            frequency = QTableWidgetItem("—")
            frequency.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 1, frequency)
        self.result.addWidget(self.table, 1)
        self.totals = wrapped_label("Всего —    Сумма частот —")
        self.result.addWidget(self.totals)

    def _update_mode(self) -> None:
        self.workers.setEnabled(self.mode.currentData() == Mode.PARALLEL)

    def _request(self) -> None:
        try:
            config = NotesConfig(count=self.count.value(), seed=seed_value(self.seed))
        except InputError as exc:
            self.controls.status.setText(str(exc))
            return
        self.requested.emit(config, Mode(self.mode.currentData()), self.workers.value())

    def show_run(self, run: NoteRun) -> None:
        summary = run.result.summary
        self.metrics.setText(
            f"{run.seconds:.3f} с  ·  Процессов {len(run.result.process_ids)} из {run.pool_workers}  ·  Seed {run.seed}"
        )
        self.metrics.show()
        self.preview.setText(" · ".join(summary.preview))
        for row, frequency in enumerate(summary.frequencies):
            self.table.item(row, 1).setText(grouped(frequency))
        self.totals.setText(f"Всего {grouped(summary.count)}    ·    Сумма частот {grouped(sum(summary.frequencies))}")
        self.controls.status.setText("Генерация завершена.")
