
import httpx

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PyQt6.QtWidgets import QMessageBox, QVBoxLayout


class StatisticsController:
    def __init__(self, window, api):
        self.window = window
        self.api = api

        self.setup_chart()

        self.window.refreshStatisticsButton.clicked.connect(
            self.load_statistics
        )

    @staticmethod
    def format_minutes(minutes):
        total = round(minutes)

        hours = total // 60
        remaining_minutes = total % 60

        return f"{hours} ч {remaining_minutes} мин"

    def setup_chart(self):
        self.figure = Figure(
            figsize=(6, 3),
            layout="constrained"
        )

        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(111)

        layout = QVBoxLayout(self.window.chartContainer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def load_statistics(self):
        try:
            statistics = self.api.get_statistics()

        except httpx.HTTPError as err:
            QMessageBox.warning(
                self.window,
                "Ошибка загрузки",
                f"Не удалось получить статистику:\n{err}"
            )
            return

        count = statistics["record_count"]

        self.update_chart(statistics["duration_by_day"])

        self.window.recordCountLabel.setText(
            f"Количество записей\n{count}"
        )

        if count == 0:
            self.window.averageDurationLabel.setText(
                "Средняя продолжительность\n—"
            )
            self.window.minDurationLabel.setText(
                "Самый короткий сон\n—"
            )
            self.window.maxDurationLabel.setText(
                "Самый долгий сон\n—"
            )
            return

        self.window.averageDurationLabel.setText(
            "Средняя продолжительность\n"
            + self.format_minutes(
                statistics["average_duration_minutes"]
            )
        )

        self.window.minDurationLabel.setText(
            "Самый короткий сон\n"
            + self.format_minutes(
                statistics["shortest_duration_minutes"]
            )
        )

        self.window.maxDurationLabel.setText(
            "Самый долгий сон\n"
            + self.format_minutes(
                statistics["longest_duration_minutes"]
            )
        )

    def update_chart(self, duration_by_day):
        self.axes.clear()

        if not duration_by_day:
            self.axes.text(
                0.5,
                0.5,
                "Нет данных для построения графика",
                ha="center",
                va="center",
                transform=self.axes.transAxes
            )

            self.axes.set_axis_off()

        else:
            self.axes.set_axis_on()

            days = duration_by_day[-14:]

            dates = [
                item["date"][8:10]
                + "."
                + item["date"][5:7]
                for item in days
            ]

            hours = [
                item["duration_minutes"] / 60
                for item in days
            ]

            self.axes.bar(dates, hours)

            self.axes.set_ylabel("Часы")
            self.axes.set_ylim(bottom=0)
            self.axes.grid(axis="y", alpha=0.2)
            self.axes.set_axisbelow(True)

            self.axes.tick_params(
                axis="x",
                labelrotation=35
            )

        self.canvas.draw_idle()
