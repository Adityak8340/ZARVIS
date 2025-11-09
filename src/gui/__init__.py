"""
ZARVIS GUI Package - Modular PyQt6 Interface
"""
import sys
from PyQt6.QtWidgets import QApplication
from .main_window import ZARVISMainWindow


def launch_gui(zarvis):
    """
    Launch the ZARVIS GUI application.
    
    Args:
        zarvis: ZARVIS instance to control
        
    Returns:
        Exit code
    """
    app = QApplication(sys.argv)
    app.setApplicationName("ZARVIS")
    
    window = ZARVISMainWindow(zarvis)
    window.show()
    
    return app.exec()


__all__ = ['launch_gui', 'ZARVISMainWindow']
