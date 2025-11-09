"""
ZARVIS GUI Module - PyQt6 Desktop Interface
"""
import sys
import os
import tempfile
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QTabWidget,
    QFileDialog, QMessageBox, QStatusBar, QGroupBox, QScrollArea, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QTextCursor
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput


class ProcessingThread(QThread):
    """Thread for running AI processing tasks without blocking UI."""
    finished = pyqtSignal(str)
    audio_ready = pyqtSignal(str)  # Signal for audio file path
    error = pyqtSignal(str)
    
    def __init__(self, zarvis, task_type: str, **kwargs):
        super().__init__()
        self.zarvis = zarvis
        self.task_type = task_type
        self.kwargs = kwargs
    
    def run(self):
        """Execute the AI task."""
        try:
            if self.task_type == "text":
                result = self.zarvis.process_text_command(
                    self.kwargs.get("text", ""),
                    self.kwargs.get("context")
                )
                self.finished.emit(result)
            
            elif self.task_type == "voice":
                # Process voice and get text response
                result = self.zarvis.process_voice_command(
                    self.kwargs.get("audio_file", "")
                )
                self.finished.emit(result)
            
            elif self.task_type == "vision":
                result = self.zarvis.analyze_image(
                    self.kwargs.get("image_url", ""),
                    self.kwargs.get("prompt")
                )
                self.finished.emit(result)
            
            elif self.task_type == "speak":
                # Generate speech and emit the audio file path
                audio_path = self.zarvis.mouth.speak(
                    self.kwargs.get("text", "")
                )
                # Convert Path to string
                self.audio_ready.emit(str(audio_path))
            
        except Exception as e:
            self.error.emit(str(e))


class AudioRecorder(QThread):
    """Thread for recording audio from microphone."""
    recording_finished = pyqtSignal(str)  # Emits the path to saved audio
    error = pyqtSignal(str)
    
    def __init__(self, duration: int = 10, sample_rate: int = 16000):
        super().__init__()
        self.duration = duration
        self.sample_rate = sample_rate
        self.recording = []
        self.is_recording = False
        self.stream = None
    
    def run(self):
        """Record audio from the microphone."""
        try:
            self.is_recording = True
            
            # Ensure output directory exists
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            
            # Create callback to collect audio chunks
            def callback(indata, frames, time, status):
                if status:
                    print(f"Recording status: {status}")
                if self.is_recording:
                    self.recording.append(indata.copy())
            
            # Start recording with input stream
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                callback=callback
            ):
                # Wait for recording to complete or be stopped
                for _ in range(self.duration * 10):  # Check every 100ms
                    if not self.is_recording:
                        break
                    self.msleep(100)
            
            # Concatenate all recorded chunks
            if self.recording:
                audio_data = np.concatenate(self.recording, axis=0)
                
                # Save to file
                import time
                timestamp = int(time.time() * 1000)
                output_file = output_dir / f"recording_{timestamp}.wav"
                sf.write(str(output_file), audio_data, self.sample_rate)
                self.recording_finished.emit(str(output_file))
            else:
                self.error.emit("No audio data recorded")
                
        except Exception as e:
            self.error.emit(f"Recording error: {str(e)}")
        finally:
            self.is_recording = False
    
    def stop_recording(self):
        """Stop the recording."""
        self.is_recording = False


class ZARVISGui(QMainWindow):
    """Main GUI window for ZARVIS."""
    
    def __init__(self, zarvis):
        super().__init__()
        self.zarvis = zarvis
        self.processing_thread: Optional[ProcessingThread] = None
        self.voice_enabled = True  # Enable voice output by default
        self.current_image_url = None  # Store current image for context
        
        # Audio player for voice output
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(1.0)  # Set volume to 100%
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)
        
        # Connect media player signals
        self.media_player.errorOccurred.connect(self.on_media_error)
        self.media_player.playbackStateChanged.connect(self.on_playback_state_changed)
        
        # Audio recorder
        self.audio_recorder: Optional[AudioRecorder] = None
        self.is_recording = False
        
        # Speech generation thread
        self.speech_thread: Optional[ProcessingThread] = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("🧠 ZARVIS - Zero-Latency AI System")
        self.setGeometry(100, 100, 1000, 700)
        
        # Set dark theme
        self.set_dark_theme()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("🧠 ZARVIS")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Zero-Latency Autonomous Runtime Virtual Intelligence System")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #888; font-size: 12px;")
        main_layout.addWidget(subtitle_label)
        
        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_chat_tab(), "💬 Chat")
        tabs.addTab(self.create_settings_tab(), "⚙️ Settings")
        main_layout.addWidget(tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        self.show()
    
    def set_dark_theme(self):
        """Apply dark theme to the application."""
        dark_stylesheet = """
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
        self.setStyleSheet(dark_stylesheet)
    
    def create_chat_tab(self) -> QWidget:
        """Create the text chat interface with multimodal capabilities."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Controls bar at top
        controls_layout = QHBoxLayout()
        
        # Voice output toggle
        self.voice_toggle = QCheckBox("🗣️ Voice Output")
        self.voice_toggle.setChecked(True)
        self.voice_toggle.stateChanged.connect(self.toggle_voice_output)
        controls_layout.addWidget(self.voice_toggle)
        
        controls_layout.addStretch()
        
        # Clear button
        clear_button = QPushButton("Clear Chat")
        clear_button.clicked.connect(self.clear_chat)
        controls_layout.addWidget(clear_button)
        
        layout.addLayout(controls_layout)
        
        # Chat history
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Consolas", 10))
        layout.addWidget(self.chat_display)
        
        # Input area with multimodal buttons
        input_layout = QHBoxLayout()
        
        # Microphone button
        self.mic_button = QPushButton("🎤")
        self.mic_button.setToolTip("Send voice message")
        self.mic_button.clicked.connect(self.record_voice_message)
        self.mic_button.setMaximumWidth(50)
        input_layout.addWidget(self.mic_button)
        
        # Image button
        self.image_button = QPushButton("🖼️")
        self.image_button.setToolTip("Attach image")
        self.image_button.clicked.connect(self.attach_image)
        self.image_button.setMaximumWidth(50)
        input_layout.addWidget(self.image_button)
        
        # Text input
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message here...")
        self.chat_input.returnPressed.connect(self.send_chat_message)
        input_layout.addWidget(self.chat_input)
        
        # Send button
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_chat_message)
        input_layout.addWidget(send_button)
        
        layout.addLayout(input_layout)
        
        # Image preview label (hidden by default)
        self.image_preview_label = QLabel()
        self.image_preview_label.setStyleSheet("color: #0e639c; padding: 5px;")
        self.image_preview_label.hide()
        layout.addWidget(self.image_preview_label)
        
        return tab
    

    
    def create_settings_tab(self) -> QWidget:
        """Create the settings interface."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
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
        
        clear_memory_btn = QPushButton("Clear Conversation Memory")
        clear_memory_btn.clicked.connect(self.clear_memory)
        layout.addWidget(clear_memory_btn)
        
        layout.addStretch()
        
        return tab
    
    def send_chat_message(self):
        """Send a chat message to ZARVIS."""
        user_message = self.chat_input.text().strip()
        if not user_message and not self.current_image_url:
            return
        
        self.chat_input.clear()
        
        # Show user message
        if self.current_image_url:
            self.append_chat(f"You: [Image attached] {user_message}", "#0e639c")
        else:
            self.append_chat(f"You: {user_message}", "#0e639c")
        
        self.status_bar.showMessage("Processing...")
        
        # Process based on whether image is attached
        if self.current_image_url:
            # Vision task
            self.processing_thread = ProcessingThread(
                self.zarvis, "vision", 
                image_url=self.current_image_url,
                prompt=user_message or "Describe what you see in detail."
            )
            self.current_image_url = None
            self.image_preview_label.hide()
        else:
            # Text task
            self.processing_thread = ProcessingThread(
                self.zarvis, "text", text=user_message
            )
        
        self.processing_thread.finished.connect(self.on_chat_response)
        self.processing_thread.error.connect(self.on_error)
        self.processing_thread.start()
    
    def on_chat_response(self, response: str):
        """Handle chat response and optionally speak it."""
        self.append_chat(f"ZARVIS: {response}", "#10a810")
        self.status_bar.showMessage("Ready")
        
        # Speak response if voice is enabled
        if self.voice_enabled and response:
            self.speak_text(response)
    
    def append_chat(self, message: str, color: str):
        """Append message to chat display."""
        self.chat_display.append(f'<span style="color: {color};">{message}</span>')
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
    
    def clear_chat(self):
        """Clear chat history."""
        self.chat_display.clear()
        self.append_chat("Chat cleared.", "#888")
    
    def toggle_voice_output(self, state):
        """Toggle voice output on/off."""
        self.voice_enabled = (state == Qt.CheckState.Checked.value)
        status = "enabled" if self.voice_enabled else "disabled"
        self.append_chat(f"[Voice output {status}]", "#888")
    
    def record_voice_message(self):
        """Record audio from microphone or stop recording."""
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.mic_button.setText("⏹️")
            self.mic_button.setStyleSheet("background-color: #ff0000;")
            self.mic_button.setEnabled(True)  # Keep button enabled for stopping
            self.append_chat("[🎤 Recording... Click stop button to finish]", "#ff8800")
            self.status_bar.showMessage("Recording... (Click stop or wait 10 sec)")
            
            # Create and start recorder
            self.audio_recorder = AudioRecorder(duration=10)
            self.audio_recorder.recording_finished.connect(self.on_recording_finished)
            self.audio_recorder.error.connect(self.on_error)
            self.audio_recorder.finished.connect(self.on_recorder_thread_finished)
            self.audio_recorder.start()
            
            # Auto-stop after timeout (if not manually stopped)
            QTimer.singleShot(10000, self.auto_stop_recording)
        else:
            # Stop recording manually
            self.stop_recording()
    
    def stop_recording(self):
        """Stop the current recording manually."""
        if self.is_recording and self.audio_recorder:
            self.audio_recorder.stop_recording()
            # Don't change UI here, wait for thread to finish
    
    def auto_stop_recording(self):
        """Auto-stop recording after timeout."""
        if self.is_recording:
            self.stop_recording()
    
    def on_recorder_thread_finished(self):
        """Called when recording thread finishes."""
        self.is_recording = False
        self.mic_button.setText("🎤")
        self.mic_button.setStyleSheet("")
        self.status_bar.showMessage("Processing audio...")
    
    def on_recording_finished(self, audio_file: str):
        """Handle recorded audio file."""
        self.append_chat("You: [🎤 Voice message recorded]", "#0e639c")
        
        # Clean up old processing thread if exists
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.wait(1000)  # Wait up to 1 second
        
        # Process voice command
        self.processing_thread = ProcessingThread(
            self.zarvis, "voice", audio_file=audio_file
        )
        self.processing_thread.finished.connect(self.on_chat_response)
        self.processing_thread.error.connect(self.on_error)
        self.processing_thread.start()
    
    def attach_image(self):
        """Attach an image URL or file for vision analysis."""
        from PyQt6.QtWidgets import QInputDialog
        
        # Ask for image URL
        image_url, ok = QInputDialog.getText(
            self,
            "Image URL",
            "Enter image URL:",
            QLineEdit.EchoMode.Normal
        )
        
        if ok and image_url.strip():
            self.current_image_url = image_url.strip()
            self.image_preview_label.setText(f"📎 Image attached: {image_url[:50]}...")
            self.image_preview_label.show()
            self.chat_input.setPlaceholderText("Ask something about the image...")
    
    def speak_text(self, text: str):
        """Generate and play speech from text."""
        self.status_bar.showMessage("Generating speech...")
        
        # Clean up old speech thread if exists
        if self.speech_thread and self.speech_thread.isRunning():
            self.speech_thread.wait(1000)
        
        # Create speech thread
        self.speech_thread = ProcessingThread(
            self.zarvis, "speak", text=text
        )
        self.speech_thread.audio_ready.connect(self.play_audio)
        self.speech_thread.error.connect(self.on_error)
        self.speech_thread.start()
    
    def play_audio(self, audio_path: str):
        """Play audio file."""
        try:
            # Check if file exists
            audio_file = Path(audio_path)
            if not audio_file.exists():
                self.append_chat(f"[Audio file not found: {audio_path}]", "#ff0000")
                self.status_bar.showMessage("Ready")
                return
            
            # Log file info for debugging
            print(f"Playing audio: {audio_file.absolute()}")
            print(f"File size: {audio_file.stat().st_size} bytes")
            
            # Stop any currently playing audio
            if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.media_player.stop()
            
            # Set source and play
            file_url = QUrl.fromLocalFile(str(audio_file.absolute()))
            print(f"Media URL: {file_url.toString()}")
            
            self.media_player.setSource(file_url)
            self.media_player.play()
            
            self.append_chat("[🔊 Playing voice response...]", "#888")
            self.status_bar.showMessage("🔊 Playing voice response...")
            
        except Exception as e:
            error_msg = f"Audio playback error: {str(e)}"
            self.append_chat(f"[{error_msg}]", "#ff0000")
            self.status_bar.showMessage("Ready")
    
    def on_media_error(self, error, error_string):
        """Handle media player errors."""
        self.append_chat(f"[Media player error: {error_string}]", "#ff0000")
        self.status_bar.showMessage("Ready")
    
    def on_playback_state_changed(self, state):
        """Handle playback state changes."""
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.status_bar.showMessage("Ready")
            self.append_chat("[✓ Voice response finished]", "#888")
    
    def clear_memory(self):
        """Clear ZARVIS memory."""
        self.zarvis.brain.clear_memory()
        QMessageBox.information(self, "Memory Cleared", "Conversation memory has been cleared.")
    
    def on_error(self, error_msg: str):
        """Handle errors."""
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")
        self.status_bar.showMessage("Error occurred")
    
    def closeEvent(self, event):
        """Clean up threads when closing the application."""
        # Stop recording if active
        if self.is_recording and self.audio_recorder:
            self.audio_recorder.stop_recording()
            self.audio_recorder.wait(2000)  # Wait up to 2 seconds
        
        # Stop processing thread if active
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.wait(2000)  # Wait up to 2 seconds
        
        # Stop speech thread if active
        if self.speech_thread and self.speech_thread.isRunning():
            self.speech_thread.wait(2000)  # Wait up to 2 seconds
        
        # Stop media player
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.stop()
        
        event.accept()


def launch_gui(zarvis):
    """Launch the ZARVIS GUI."""
    app = QApplication(sys.argv)
    app.setApplicationName("ZARVIS")
    
    _ = ZARVISGui(zarvis)  # Window is kept alive by Qt
    
    return app.exec()
