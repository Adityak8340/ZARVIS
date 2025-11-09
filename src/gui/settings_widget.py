"""
Settings Widget for ZARVIS GUI
Displays configuration and settings information.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal


class SettingsWidget(QWidget):
    """Settings and configuration display widget."""
    
    clear_memory = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the settings interface."""
        layout = QVBoxLayout(self)
        
        # Settings information
        settings_info = QLabel(
            "⚙️ ZARVIS Settings\n\n"
            "API Key: Configured via .env file\n"
            "Models: Using Groq's latest models\n\n"
            "🧠 Brain: meta-llama/llama-4-scout-17b-16e-instruct\n"
            "👁️ Eye: meta-llama/llama-4-scout-17b-16e-instruct\n"
            "👂 Ear: whisper-large-v3\n"
            "🗣️ Mouth: playai-tts (Aaliyah-PlayAI)\n\n"
            "Features:\n"
            "• Text chat with AI\n"
            "• Voice input via microphone button\n"
            "• Image analysis via image button\n"
            "• Automatic voice responses (toggle in chat)\n"
        )
        settings_info.setWordWrap(True)
        layout.addWidget(settings_info)
        
        # Clear memory button
        clear_memory_btn = QPushButton("Clear Conversation Memory")
        clear_memory_btn.clicked.connect(self.clear_memory.emit)
        layout.addWidget(clear_memory_btn)
        
        layout.addStretch()
