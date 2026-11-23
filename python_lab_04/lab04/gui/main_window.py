from collections.abc import Callable

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QLabel, QMainWindow, QMessageBox, QTabWidget, QVBoxLayout, QWidget

from ..core.benchmark import compare
from ..core.generation import Mode, run_notes
from ..core.notes import NotesConfig
from .benchmark_tab import BenchmarkTab
from .exercise_tabs import EmailsTab, MultiplesTab
from .notes_tab import NotesTab
from .widgets import RunControls
from .workers import Operation, OperationWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Генераторы Python · Лабораторная работа № 4")
        self.resize(1050, 710)
        self.setMinimumSize(820, 650)
        self._worker: OperationWorker | None = None
        self._active: RunControls | None = None
        self._closing = False

        file_menu = self.menuBar().addMenu("Файл")
        quit_action = file_menu.addAction("Выход")
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        help_menu = self.menuBar().addMenu("Справка")
        help_menu.addAction("О программе", self._about)

        root = QWidget()
        root.setObjectName("appRoot")
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(22, 16, 22, 22)
        layout.setSpacing(6)
        title = QLabel("Генераторы и встроенные функции Python")
        title.setObjectName("title")
        layout.addWidget(title)
        subtitle = QLabel("Лабораторная работа № 4 - Вариант 20")
        subtitle.setObjectName("muted")
        layout.addWidget(subtitle)
        layout.addSpacing(12)

        self.tabs = QTabWidget()
        self.notes = NotesTab()
        self.multiples = MultiplesTab()
        self.emails = EmailsTab()
        self.benchmark = BenchmarkTab()
        self.tabs.addTab(self.notes, "Генератор нот")
        self.tabs.addTab(self.multiples, "Числа, кратные 3")
        self.tabs.addTab(self.emails, "Проверка email")
        self.tabs.addTab(self.benchmark, "Производительность")
        layout.addWidget(self.tabs, 1)

        self.notes.requested.connect(self._generate_notes)
        self.benchmark.requested.connect(self._compare_modes)
        self._work_tabs = (self.notes, self.benchmark)
        for tab in self._work_tabs:
            tab.controls.stop_requested.connect(self._request_stop)

    def _about(self) -> None:
        QMessageBox.about(
            self,
            "О программе",
            "Лабораторная работа № 4 по теории алгоритмов, вариант 20.\n\n"
            "Ноты, числа, кратные трём, и фильтрация email. Во вкладке «Производительность» "
            "можно сравнить последовательный режим и пул процессов.",
        )

    def _generate_notes(self, config: NotesConfig, mode: Mode, workers: int) -> None:
        self._start(
            self.notes.controls,
            lambda cancel, progress: run_notes(config, mode, workers, cancel, progress),
            self.notes.show_run,
        )

    def _compare_modes(self, config: NotesConfig, workers: int, repeats: int) -> None:
        self._start(
            self.benchmark.controls,
            lambda cancel, progress: compare(config, workers, repeats, cancel=cancel, progress=progress),
            self.benchmark.show_benchmark,
        )

    def _start(self, active: RunControls, operation: Operation, show_result: Callable) -> None:
        if self._worker is not None:
            return
        worker = OperationWorker(operation, self)
        self._worker = worker
        self._active = active
        for tab in self._work_tabs:
            tab.set_busy(True, tab.controls is active)
        worker.progress.connect(self._progress)
        worker.succeeded.connect(show_result)
        worker.failed.connect(self._operation_error)
        worker.cancelled.connect(self._operation_error)
        worker.finished.connect(self._operation_finished)
        worker.start()

    def _progress(self, completed: int, total: int) -> None:
        if self._active is not None and self._active.stop.isEnabled():
            self._active.update_progress(completed, total)

    def _operation_error(self, message: str) -> None:
        if self._active is not None:
            self._active.status.setText(message)

    def _request_stop(self) -> None:
        if self._worker is not None and self._active is not None:
            self._worker.request_stop()
            self._active.stopping()

    def _operation_finished(self) -> None:
        assert self._worker is not None
        self._worker.deleteLater()
        self._worker = None
        self._active = None
        for tab in self._work_tabs:
            tab.set_busy(False, False)
        if self._closing:
            QTimer.singleShot(0, self.close)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._worker is not None:
            self._closing = True
            self._request_stop()
            event.ignore()
        else:
            super().closeEvent(event)
