from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout

from ..core.benchmark import (
    DEFAULT_CPU_COUNT, DEFAULT_CPU_ROUNDS, DEFAULT_REPEATS, MAX_REPEATS, BenchmarkResult,
)
from ..core.errors import InputError
from ..core.generation import Mode
from ..core.notes import DEFAULT_COUNT, MAX_COUNT, MAX_ROUNDS, NotesConfig
from ..core.parallel import default_workers, max_workers
from .widgets import WorkTab, grouped, seed_field, seed_value, spin, wrapped_label


class BenchmarkTab(WorkTab):
    requested = pyqtSignal(object, int, int)

    def __init__(self) -> None:
        super().__init__(
            "Медианы рассчитаны по замерам после прогрева. Время подготовки пула показано отдельно.",
            "Медианное время",
            "Сравнить производительность",
        )
        self.scenario = QComboBox()
        self.scenario.addItem("А · Стандартная", False)
        self.scenario.addItem("Б · Нагрузка SHA-256", True)
        self.count = spin(1, MAX_COUNT, DEFAULT_COUNT)
        self.seed = seed_field()
        self.workers = spin(1, max_workers(), default_workers())
        self.rounds = spin(1, MAX_ROUNDS, DEFAULT_CPU_ROUNDS)
        self.rounds.setEnabled(False)
        self.repeats = spin(1, MAX_REPEATS, DEFAULT_REPEATS)
        self.form.addRow("Сценарий", self.scenario)
        self.form.addRow("Количество нот", self.count)
        self.form.addRow("Seed", self.seed)
        self.form.addRow("Процессов в пуле", self.workers)
        self.form.addRow("Итераций на ноту", self.rounds)
        self.form.addRow("Повторов", self.repeats)
        self.scenario.currentIndexChanged.connect(self._update_scenario)
        self.controls.requested.connect(self._request)

        self.comparison = wrapped_label("Запустите сравнение для просмотра замеров.")
        self.comparison.setObjectName("metrics")
        self.result.addWidget(self.comparison)
        graph = QVBoxLayout()
        graph.setSpacing(14)
        self.rows = {}
        for mode in Mode:
            labels = QHBoxLayout()
            labels.addWidget(QLabel(mode.label))
            labels.addStretch(1)
            value = QLabel("—")
            labels.addWidget(value)
            graph.addLayout(labels)
            bar = QProgressBar()
            bar.setObjectName(mode.value)
            bar.setRange(0, 1000)
            bar.setTextVisible(False)
            graph.addWidget(bar)
            self.rows[mode] = bar, value
        self.result.addLayout(graph)
        self.setup = wrapped_label()
        self.setup.setObjectName("muted")
        self.result.addWidget(self.setup)
        self.workload = wrapped_label()
        self.workload.setObjectName("muted")
        self.result.addWidget(self.workload)
        self.explanation = wrapped_label()
        self.result.addWidget(self.explanation)
        self.result.addStretch(1)

    def _update_scenario(self) -> None:
        cpu = self.scenario.currentData()
        self.rounds.setEnabled(cpu)
        self.count.setValue(DEFAULT_CPU_COUNT if cpu else DEFAULT_COUNT)

    def _request(self) -> None:
        rounds = self.rounds.value() if self.scenario.currentData() else 0
        try:
            config = NotesConfig(count=self.count.value(), seed=seed_value(self.seed), rounds=rounds)
        except InputError as exc:
            self.controls.status.setText(str(exc))
            return
        self.requested.emit(config, self.workers.value(), self.repeats.value())

    def show_benchmark(self, benchmark: BenchmarkResult) -> None:
        sequential, parallel = benchmark.sequential, benchmark.parallel
        speedup, saved = benchmark.speedup, benchmark.time_saved_percent
        assert sequential is not None and parallel is not None and speedup is not None and saved is not None
        scale = max(sequential.median_seconds, parallel.median_seconds)
        for measurement in sequential, parallel:
            bar, label = self.rows[measurement.mode]
            bar.setValue(round(1000 * measurement.median_seconds / scale))
            label.setText(f"{measurement.median_seconds:.6f} с")
        self.comparison.setText(f"Ускорение {speedup:.3f}×    ·    Экономия времени {saved:+.2f} %")
        self.setup.setText(
            f"Подготовка пула {benchmark.pool_setup_seconds:.3f} с    ·    "
            f"Процессов с пакетами {parallel.process_count} из {benchmark.pool_workers}    ·    Seed {benchmark.seed}"
        )
        rounds = self.rounds.value() if self.scenario.currentData() else 0
        self.workload.setText(
            f"Нот {grouped(self.count.value())}    ·    Итераций на ноту {rounds}    ·    Замеров {len(sequential.samples)}"
        )
        self.explanation.setText(benchmark.explanation)
        self.controls.status.setText("Сравнение завершено.")
