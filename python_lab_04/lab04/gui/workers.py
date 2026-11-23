import logging
from collections.abc import Callable
from threading import Event
from time import perf_counter

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget

from ..core.errors import Cancelled, LabError
from ..core.notes import Progress

Operation = Callable[[Event, Progress], object]
logger = logging.getLogger(__name__)

# Выполняет длительные операции в фоновом потоке, чтобы не блокировать основной поток интерфейса.
class OperationWorker(QThread):
    # Сигналы передают в главный поток прогресс, результат вычисления, ошибку или сообщение об отмене.
    # Сигналы подключены в main_window.py
    progress = pyqtSignal(object, object)
    succeeded = pyqtSignal(object)
    failed = pyqtSignal(str)
    cancelled = pyqtSignal(str)

    def __init__(self, operation: Operation, parent: QWidget) -> None:
        super().__init__(parent)
        self._operation = operation # ф-я, которую требуется выпонлить
        self._cancel = Event()
        self._last_update = 0.0

    def request_stop(self) -> None:
        self._cancel.set()

    # Ограничиваем частоту отправки прогресса примерно до 16 раз/с, чтобы не перегружать интерфейс лишними обновлениями.
    # Финальное значение отправляем обязательно.
    def _report_progress(self, completed: int, total: int) -> None:
        now = perf_counter()
        if completed == total or now - self._last_update >= 0.06:
            self._last_update = now
            self.progress.emit(completed, total)

    # Запускаем переданную операцию в фоновом потоке.
    # По завершении отправляем результат или сообщение об ошибке
    def run(self) -> None:
        try:
            # После каждого обработанного пакета вызываем callback progress.
            # Он передаёт текущий прогресс в OperationWorker, который ограничивает частоту обновлений интерфейса.
            result = self._operation(self._cancel, self._report_progress)
        except Cancelled as exc:
            self.cancelled.emit(str(exc))
        except LabError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:
            logger.exception("Ошибка фонового вычисления")
            self.failed.emit(f"Вычисление завершилось с ошибкой. Проверьте параметры и повторите запуск. {exc}")
        else:
            self.succeeded.emit(result)
