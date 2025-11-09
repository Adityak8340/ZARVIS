"""
Styling and Theming for ZARVIS GUI
Contains stylesheet definitions and UI styling constants.
"""


class DarkTheme:
    """Dark theme stylesheet for ZARVIS GUI."""
    
    STYLESHEET = """
        QMainWindow {
            background-color: #1e1e1e;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QTextEdit, QLineEdit {
            background-color: #2d2d2d;
            border: 1px solid #3d3d3d;
            border-radius: 5px;
            padding: 5px;
            color: #ffffff;
        }
        QPushButton {
            background-color: #0e639c;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
            color: white;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1177bb;
        }
        QPushButton:pressed {
            background-color: #0d5a8a;
        }
        QPushButton:disabled {
            background-color: #3d3d3d;
            color: #888;
        }
        QLabel {
            color: #ffffff;
        }
        QTabWidget::pane {
            border: 1px solid #3d3d3d;
            background-color: #1e1e1e;
        }
        QTabBar::tab {
            background-color: #2d2d2d;
            color: #ffffff;
            padding: 8px 20px;
            border: 1px solid #3d3d3d;
        }
        QTabBar::tab:selected {
            background-color: #0e639c;
        }
        QStatusBar {
            background-color: #2d2d2d;
            color: #888;
        }
        QGroupBox {
            border: 1px solid #3d3d3d;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            color: #0e639c;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
    """
    
    # Color constants
    USER_MESSAGE = "#0e639c"
    AI_MESSAGE = "#10a810"
    SYSTEM_MESSAGE = "#888"
    ERROR_MESSAGE = "#ff0000"
    WARNING_MESSAGE = "#ff8800"


class Fonts:
    """Font configurations."""
    
    TITLE_SIZE = 24
    SUBTITLE_SIZE = 12
    CHAT_SIZE = 10
    CHAT_FONT = "Consolas"
