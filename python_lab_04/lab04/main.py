import multiprocessing
import sys


def main() -> int:
    from PyQt6.QtWidgets import QApplication

    # относительные импорты
    from .gui.main_window import MainWindow
    from .gui.styles import STYLESHEET

    app = QApplication(sys.argv)

    app.setApplicationName("Генераторы Python")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.show()

    # Запускаем цикл событий Qt
    return app.exec()


# freeze_support() обеспечивает совместимость с упакованными
# приложениями, использующими multiprocessing.
if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
