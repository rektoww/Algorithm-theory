STYLESHEET = """
QWidget {
    color: #172a43;
    font-family: 'Segoe UI';
    font-size: 14px;
}
QWidget#appRoot, QMenuBar { background: #eef3f8; }
QLabel#title { color: #132845; font-size: 25px; font-weight: 700; }
QLabel#muted { color: #455a73; }
QLabel#metrics { color: #164576; font-size: 15px; font-weight: 700; min-height: 24px; }
QLabel#preview { background: #eff5fc; border: 1px solid #dbe6f4; border-radius: 6px; padding: 10px; }
QTabWidget::pane { background: #f7f9fc; border: 1px solid #d4deeb; border-radius: 7px; }
QTabBar::tab {
    background: #e7eef6;
    border: 1px solid #d4deeb;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 9px 16px;
    margin-right: 4px;
}
QTabBar::tab:selected { background: #f7f9fc; color: #154a82; border-top: 3px solid #2a69ac; }
QGroupBox {
    background: #ffffff;
    border: 1px solid #d4deeb;
    border-radius: 8px;
    padding: 13px 12px 8px;
    margin-top: 10px;
    font-weight: 600;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; background: #f7f9fc; }
QLineEdit, QComboBox, QPlainTextEdit, QTableWidget {
    background: #ffffff;
    border: 1px solid #c9d6e6;
    border-radius: 5px;
    padding: 5px 8px;
    selection-background-color: #275f9d;
    selection-color: #ffffff;
}
QLineEdit, QSpinBox, QComboBox { min-height: 19px; }
QSpinBox { min-height: 28px; }
QComboBox { padding-right: 21px; }
QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus { border-color: #2766a9; }
QTableWidget { padding: 0; alternate-background-color: #f3f7fb; gridline-color: #e6edf5; }
QTableWidget::item { padding: 0 10px; }
QHeaderView::section { background: #eaf1fa; border: 0; padding: 6px 10px; font-weight: 600; }
QPushButton { background: #f5f8fc; border: 1px solid #c9d6e6; border-radius: 6px; padding: 8px 11px; }
QPushButton:hover { background: #eaf2fb; border-color: #9cb6d4; }
QPushButton#primary { background: #245f9f; color: #ffffff; border-color: #245f9f; font-weight: 600; }
QPushButton#primary:hover { background: #1e5189; }
QPushButton:focus { border-color: #165189; }
QPushButton#primary:focus { border-color: #12365b; }
QPushButton:disabled, QPushButton#primary:disabled {
    color: #617288;
    background: #eaf0f6;
    border-color: #d4deeb;
}
QProgressBar { background: #e9eff6; border: 0; border-radius: 5px; min-height: 10px; max-height: 10px; }
QProgressBar::chunk { background: #2a69ac; border-radius: 5px; }
QProgressBar#sequential, QProgressBar#parallel { min-height: 16px; max-height: 16px; }
QProgressBar#sequential::chunk { background: #778da8; }
"""
