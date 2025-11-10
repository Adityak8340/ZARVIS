"""
Main Window for ZARVIS GUI
Coordinates all widgets and handles application logic.
"""
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QTabWidget, QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QFont
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from .chat_widget import ChatWidget
from .settings_widget import SettingsWidget
from .threads import ProcessingThread, AudioRecorder
from .styles import DarkTheme, Fonts
from .audio_handler import AudioHandlerMixin


class ZARVISMainWindow(AudioHandlerMixin, QMainWindow):
    """Main window for ZARVIS GUI application."""
    
    def __init__(self, zarvis):
        """
        Initialize main window.
        
        Args:
            zarvis: ZARVIS instance to control
        """
        super().__init__()
        self.zarvis = zarvis
        
        # Thread management
        self.processing_thread: Optional[ProcessingThread] = None
        self.audio_recorder: Optional[AudioRecorder] = None
        self.speech_thread: Optional[ProcessingThread] = None
        
        # State
        self.voice_enabled = True
        self.is_recording = False
        self.current_audio_file: Optional[str] = None  # Track current audio for cleanup
        
        # Audio player
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(1.0)
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.errorOccurred.connect(self._on_media_error)
        self.media_player.playbackStateChanged.connect(self._on_playback_state_changed)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("🧠 ZARVIS - Zero-Latency AI System")
        self.setGeometry(100, 100, 1000, 700)
        
        # Apply dark theme
        self.setStyleSheet(DarkTheme.STYLESHEET)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("🧠 ZARVIS")
        title_font = QFont("Arial", Fonts.TITLE_SIZE, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Zero-Latency Autonomous Runtime Virtual Intelligence System")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"color: {DarkTheme.SYSTEM_MESSAGE}; font-size: {Fonts.SUBTITLE_SIZE}px;")
        main_layout.addWidget(subtitle_label)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Chat tab
        self.chat_widget = ChatWidget()
        self.chat_widget.send_message.connect(self._handle_send_message)
        self.chat_widget.start_recording.connect(self._start_recording)
        self.chat_widget.stop_recording.connect(self._stop_recording)
        self.chat_widget.voice_toggle_changed.connect(self._toggle_voice)
        self.chat_widget.clear_chat.connect(self._clear_chat)
        tabs.addTab(self.chat_widget, "💬 Chat")
        
        # Settings tab
        settings_widget = SettingsWidget()
        settings_widget.clear_memory.connect(self._clear_memory)
        tabs.addTab(settings_widget, "⚙️ Settings")
        
        main_layout.addWidget(tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _handle_send_message(self, message: str, image_url: str):
        """Handle message send from chat widget."""
        # Display user message
        if image_url:
            self.chat_widget.append_message(
                f"You: [Image attached] {message}", 
                DarkTheme.USER_MESSAGE
            )
        else:
            self.chat_widget.append_message(
                f"You: {message}", 
                DarkTheme.USER_MESSAGE
            )
        
        self.status_bar.showMessage("Processing...")
        
        # Clean up old thread
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.wait(1000)
        
        # Process based on input type
        if image_url:
            self.processing_thread = ProcessingThread(
                self.zarvis, "vision",
                image_url=image_url,
                prompt=message or "Describe what you see in detail."
            )
        else:
            self.processing_thread = ProcessingThread(
                self.zarvis, "text", text=message
            )
        
        self.processing_thread.finished.connect(self._on_response)
        self.processing_thread.error.connect(self._on_error)
        self.processing_thread.start()
    
    def _on_response(self, response: str):
        """Handle AI response."""
        self.chat_widget.append_message(
            f"ZARVIS: {response}", 
            DarkTheme.AI_MESSAGE
        )
        self.status_bar.showMessage("Ready")
        
        # Speak response if enabled
        if self.voice_enabled and response:
            self._speak_text(response)
    
    def _toggle_voice(self, enabled: bool):
        """Toggle voice output."""
        self.voice_enabled = enabled
        status = "enabled" if enabled else "disabled"
        self.chat_widget.append_message(
            f"[Voice output {status}]", 
            DarkTheme.SYSTEM_MESSAGE
        )
    
    def _clear_chat(self):
        """Clear chat history."""
        self.chat_widget.clear_display()
    
    def _clear_memory(self):
        """Clear ZARVIS conversation memory."""
        self.zarvis.brain.clear_memory()
        QMessageBox.information(
            self, "Memory Cleared", 
            "Conversation memory has been cleared."
        )
    
    def _on_error(self, error_msg: str):
        """Handle errors."""
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")
        self.status_bar.showMessage("Error occurred")
    
    def closeEvent(self, event):
        """Clean up threads when closing."""
        # Stop recording
        if self.is_recording and self.audio_recorder:
            self.audio_recorder.stop_recording()
            self.audio_recorder.wait(2000)
        
        # Stop threads
        for thread in [self.processing_thread, self.speech_thread]:
            if thread and thread.isRunning():
                thread.wait(2000)
        
        # Stop media player
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.stop()
        
        event.accept()
