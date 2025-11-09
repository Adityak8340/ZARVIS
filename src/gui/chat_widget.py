"""
Chat Widget for ZARVIS GUI
Handles the chat interface with multimodal capabilities.
"""
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QLineEdit, QPushButton, QLabel, QCheckBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor
from .styles import DarkTheme, Fonts


class ChatWidget(QWidget):
    """Chat interface widget with voice and vision capabilities."""
    
    # Signals
    send_message = pyqtSignal(str, str)  # message, image_url
    start_recording = pyqtSignal()
    stop_recording = pyqtSignal()
    voice_toggle_changed = pyqtSignal(bool)
    clear_chat = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_image_url = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the chat interface."""
        layout = QVBoxLayout(self)
        
        # Controls bar
        controls_layout = QHBoxLayout()
        
        self.voice_toggle = QCheckBox("🗣️ Voice Output")
        self.voice_toggle.setChecked(True)
        self.voice_toggle.stateChanged.connect(self._on_voice_toggle)
        controls_layout.addWidget(self.voice_toggle)
        
        controls_layout.addStretch()
        
        clear_button = QPushButton("Clear Chat")
        clear_button.clicked.connect(self.clear_chat.emit)
        controls_layout.addWidget(clear_button)
        
        layout.addLayout(controls_layout)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont(Fonts.CHAT_FONT, Fonts.CHAT_SIZE))
        layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        
        # Microphone button
        self.mic_button = QPushButton("🎤")
        self.mic_button.setToolTip("Record voice message")
        self.mic_button.setMaximumWidth(50)
        self.mic_button.clicked.connect(self._on_mic_clicked)
        input_layout.addWidget(self.mic_button)
        
        # Image button
        image_button = QPushButton("🖼️")
        image_button.setToolTip("Attach image")
        image_button.setMaximumWidth(50)
        image_button.clicked.connect(self._on_image_clicked)
        input_layout.addWidget(image_button)
        
        # Text input
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message here...")
        self.chat_input.returnPressed.connect(self._on_send_clicked)
        input_layout.addWidget(self.chat_input)
        
        # Send button
        send_button = QPushButton("Send")
        send_button.clicked.connect(self._on_send_clicked)
        input_layout.addWidget(send_button)
        
        layout.addLayout(input_layout)
        
        # Image preview
        self.image_preview_label = QLabel()
        self.image_preview_label.setStyleSheet(f"color: {DarkTheme.USER_MESSAGE}; padding: 5px;")
        self.image_preview_label.hide()
        layout.addWidget(self.image_preview_label)
        
        self.is_recording = False
    
    def append_message(self, message: str, color: str):
        """Append a message to the chat display."""
        self.chat_display.append(f'<span style="color: {color};">{message}</span>')
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
    
    def clear_display(self):
        """Clear the chat display."""
        self.chat_display.clear()
        self.append_message("Chat cleared.", DarkTheme.SYSTEM_MESSAGE)
    
    def set_recording_state(self, recording: bool):
        """Update UI for recording state."""
        self.is_recording = recording
        if recording:
            self.mic_button.setText("⏹️")
            self.mic_button.setStyleSheet("background-color: #ff0000;")
        else:
            self.mic_button.setText("🎤")
            self.mic_button.setStyleSheet("")
    
    def _on_voice_toggle(self, state):
        """Handle voice toggle change."""
        enabled = (state == Qt.CheckState.Checked.value)
        self.voice_toggle_changed.emit(enabled)
    
    def _on_mic_clicked(self):
        """Handle microphone button click."""
        if self.is_recording:
            self.stop_recording.emit()
        else:
            self.start_recording.emit()
    
    def _on_image_clicked(self):
        """Handle image button click."""
        image_url, ok = QInputDialog.getText(
            self, "Image URL", "Enter image URL:", QLineEdit.EchoMode.Normal
        )
        if ok and image_url.strip():
            self.current_image_url = image_url.strip()
            self.image_preview_label.setText(f"📎 Image attached: {image_url[:50]}...")
            self.image_preview_label.show()
            self.chat_input.setPlaceholderText("Ask something about the image...")
    
    def _on_send_clicked(self):
        """Handle send button click."""
        message = self.chat_input.text().strip()
        if not message and not self.current_image_url:
            return
        
        self.chat_input.clear()
        image_url = self.current_image_url
        self.current_image_url = None
        self.image_preview_label.hide()
        self.chat_input.setPlaceholderText("Type your message here...")
        
        self.send_message.emit(message, image_url or "")
