from multiprocessing import active_children
from time import monotonic

import pytest

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from lab04.core.generation import Mode
from lab04.core.parallel import max_workers
from lab04.gui.main_window import MainWindow
from lab04.gui.styles import STYLESHEET


@pytest.fixture(scope="module")
def app():
    application = QApplication(["lab04-tests", "-platform", "offscreen"])
    application.setStyle("Fusion")
    application.setStyleSheet(STYLESHEET)
    yield application


def wait_for(condition, timeout=15):
    deadline = monotonic() + timeout
    while not condition():
        assert monotonic() < deadline, "Окно не достигло ожидаемого состояния"
        QTest.qWait(10)


@pytest.fixture
def window(app):
    window = MainWindow()
    window.show()
    yield window
    window.close()
    wait_for(lambda: not window.isVisible())


def test_three_tabs_and_the_benchmark(window):
    assert window.tabs.count() == 4
    assert window.multiples.values.toPlainText().startswith("-99  ·  -96")
    window.multiples.start.setText("wrong")
    window.multiples.generate.click()
    assert "целое число" in window.multiples.status.text()
    window.multiples.start.setText("7")
    window.multiples.count.setValue(3)
    window.multiples.generate.click()
    assert window.multiples.values.toPlainText() == "9  ·  12  ·  15"

    window.emails.check.click()
    assert "хотя бы один" in window.emails.status.text()
    window.emails.example.click()
    window.emails.check.click()
    assert len(window.emails.accepted.toPlainText().splitlines()) == 3
    assert "login@mail" in window.emails.rejected.toPlainText()
    assert "Отклонено 6" in window.emails.status.text()

    tab = window.notes
    tab.count.setValue(20_003)
    tab.seed.setText("invalid seed")
    tab.controls.start.click()
    assert "целое число" in tab.controls.status.text()
    tab.seed.setText("42")
    tab.controls.start.click()
    assert not window.benchmark.controls.start.isEnabled()
    wait_for(tab.controls.start.isEnabled)
    preview = tab.preview.text()
    counts = [tab.table.item(row, 1).text() for row in range(tab.table.rowCount())]
    tab.mode.setCurrentIndex(1)
    tab.workers.setValue(min(2, max_workers()))
    tab.controls.start.click()
    wait_for(tab.controls.start.isEnabled)
    assert tab.controls.status.text() == "Генерация завершена."
    assert tab.preview.text() == preview and len(preview.split("·")) == 20
    assert [tab.table.item(row, 1).text() for row in range(tab.table.rowCount())] == counts
    assert "Сумма частот 20\u202f003" in tab.totals.text()

    benchmark = window.benchmark
    benchmark.scenario.setCurrentIndex(1)
    assert benchmark.rounds.isEnabled()
    benchmark.count.setValue(5001)
    benchmark.rounds.setValue(3)
    benchmark.repeats.setValue(2)
    benchmark.controls.start.click()
    wait_for(benchmark.controls.start.isEnabled)
    assert "Ускорение" in benchmark.comparison.text()
    assert benchmark.rows[Mode.PARALLEL][0].value() > 0
    assert benchmark.rows[Mode.SEQUENTIAL][0].value() > 0


@pytest.mark.parametrize("close_window", [False, True])
def test_parallel_operation_can_stop_or_close_while_window_responds(window, close_window):
    children = {child.pid for child in active_children()}
    tab = window.notes
    tab.count.setValue(20_000_000)
    tab.mode.setCurrentIndex(1)
    tab.workers.setValue(min(2, max_workers()))
    ticks = []
    timer = QTimer(window)
    timer.timeout.connect(lambda: ticks.append(True))
    timer.start(10)
    tab.controls.start.click()
    wait_for(lambda: tab.controls.status.text().startswith("Обработано"))
    window.tabs.setCurrentWidget(window.multiples)
    window.multiples.start.setText("1")
    window.multiples.generate.click()
    assert window.multiples.values.toPlainText().startswith("3  ·  6")
    assert len(ticks) >= 2
    if close_window:
        window.close()
        wait_for(lambda: not window.isVisible())
    else:
        tab.controls.stop.click()
        wait_for(tab.controls.start.isEnabled)
        assert "остановлена" in tab.controls.status.text()
    timer.stop()
    assert {child.pid for child in active_children()} <= children
