from pathlib import Path

from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow

from .activity import ActivityController
from .api_client import SleepTrackerAPI
from .records import RecordsController
from .statistics import StatisticsController


class SleepTrackerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_path = Path(__file__).with_name("main_window.ui")
        uic.loadUi(str(ui_path), self)

        self.setWindowTitle("Sleep Tracker")

        self.api = SleepTrackerAPI()

        self.records = RecordsController(self, self.api)
        self.statistics = StatisticsController(self, self.api)
        self.activity = ActivityController(self, self.api)

        self.actionExit.triggered.connect(self.close)

        self.tabWidget.currentChanged.connect(
            self.on_tab_changed
        )

        self.records.load_records()
        self.statistics.load_statistics()
        self.activity.load_activity_log()

    def on_tab_changed(self, index):
        current_tab = self.tabWidget.widget(index)

        if current_tab == self.statisticsTab:
            self.statistics.load_statistics()

        elif current_tab == self.activityTab:
            self.activity.load_activity_log()