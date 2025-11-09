"""
Audio Handler Mixin for Main Window
Handles voice recording and playback functionality.
"""
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Any
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer
from .threads import ProcessingThread, AudioRecorder
from .styles import DarkTheme

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QStatusBar
    from .chat_widget import ChatWidget


class AudioHandlerMixin:
    """
    Mixin class for audio recording and playback.
    
    This mixin expects the parent class to have:
    - zarvis: ZARVIS instance with brain, ear, mouth, eye modules
    - chat_widget: ChatWidget instance
    - status_bar: QStatusBar instance
    - media_player: QMediaPlayer instance
    - audio_recorder: Optional AudioRecorder thread
    - processing_thread: Optional ProcessingThread
    - speech_thread: Optional ProcessingThread
    - is_recording: bool flag
    - voice_enabled: bool flag
    - _on_error(str): error handler method
    - _on_response(str): response handler method
    """
    
    # Type hints for attributes that must exist in parent class
    zarvis: Any  # ZARVIS instance with brain, ear, mouth, eye modules
    chat_widget: 'ChatWidget'
    status_bar: 'QStatusBar'
    media_player: QMediaPlayer
    audio_recorder: Optional[AudioRecorder]
    processing_thread: Optional[ProcessingThread]
    speech_thread: Optional[ProcessingThread]
    is_recording: bool
    voice_enabled: bool
    
    # Methods that must exist in parent class
    def _on_error(self, error: str) -> None:
        """Handle errors (must be implemented by parent)."""
        ...
    
    def _on_response(self, response: str) -> None:
        """Handle responses (must be implemented by parent)."""
        ...
    
    def _start_recording(self):
        """Start audio recording."""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.chat_widget.set_recording_state(True)
        self.chat_widget.append_message(
            "[🎤 Recording... Click stop button to finish]",
            DarkTheme.WARNING_MESSAGE
        )
        self.status_bar.showMessage("Recording... (Click stop or wait 10 sec)")
        
        # Create and start recorder
        self.audio_recorder = AudioRecorder(duration=10)
        self.audio_recorder.recording_finished.connect(self._on_recording_finished)
        self.audio_recorder.error.connect(self._on_error)
        self.audio_recorder.finished.connect(self._on_recorder_finished)
        self.audio_recorder.start()
        
        # Auto-stop after timeout
        QTimer.singleShot(10000, self._auto_stop_recording)
    
    def _stop_recording(self):
        """Stop audio recording manually."""
        if self.is_recording and self.audio_recorder:
            self.audio_recorder.stop_recording()
    
    def _auto_stop_recording(self):
        """Auto-stop recording after timeout."""
        if self.is_recording:
            self._stop_recording()
    
    def _on_recorder_finished(self):
        """Handle recorder thread finished."""
        self.is_recording = False
        self.chat_widget.set_recording_state(False)
        self.status_bar.showMessage("Processing audio...")
    
    def _on_recording_finished(self, audio_file: str):
        """Handle recorded audio file."""
        self.chat_widget.append_message(
            "You: [🎤 Voice message recorded]",
            DarkTheme.USER_MESSAGE
        )
        
        # Clean up old thread
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.wait(1000)
        
        # Process voice command
        self.processing_thread = ProcessingThread(
            self.zarvis, "voice", audio_file=audio_file
        )
        self.processing_thread.finished.connect(self._on_response)
        self.processing_thread.error.connect(self._on_error)
        self.processing_thread.start()
    
    def _speak_text(self, text: str):
        """Generate and play speech from text."""
        self.status_bar.showMessage("Generating speech...")
        
        # Clean up old speech thread
        if self.speech_thread and self.speech_thread.isRunning():
            self.speech_thread.wait(1000)
        
        # Create speech thread
        self.speech_thread = ProcessingThread(
            self.zarvis, "speak", text=text
        )
        self.speech_thread.audio_ready.connect(self._play_audio)
        self.speech_thread.error.connect(self._on_error)
        self.speech_thread.start()
    
    def _play_audio(self, audio_path: str):
        """Play audio file."""
        try:
            audio_file = Path(audio_path)
            if not audio_file.exists():
                self.chat_widget.append_message(
                    f"[Audio file not found: {audio_path}]",
                    DarkTheme.ERROR_MESSAGE
                )
                self.status_bar.showMessage("Ready")
                return
            
            # Debug info
            print(f"Playing audio: {audio_file.absolute()}")
            print(f"File size: {audio_file.stat().st_size} bytes")
            
            # Stop current playback
            if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.media_player.stop()
            
            # Play audio
            file_url = QUrl.fromLocalFile(str(audio_file.absolute()))
            self.media_player.setSource(file_url)
            self.media_player.play()
            
            self.chat_widget.append_message(
                "[🔊 Playing voice response...]",
                DarkTheme.SYSTEM_MESSAGE
            )
            self.status_bar.showMessage("🔊 Playing voice response...")
            
        except Exception as e:
            error_msg = f"Audio playback error: {str(e)}"
            self.chat_widget.append_message(
                f"[{error_msg}]",
                DarkTheme.ERROR_MESSAGE
            )
            self.status_bar.showMessage("Ready")
    
    def _on_media_error(self, _error, error_string):
        """Handle media player errors."""
        self.chat_widget.append_message(
            f"[Media player error: {error_string}]",
            DarkTheme.ERROR_MESSAGE
        )
        self.status_bar.showMessage("Ready")
    
    def _on_playback_state_changed(self, state):
        """Handle playback state changes."""
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.status_bar.showMessage("Ready")
            self.chat_widget.append_message(
                "[✓ Voice response finished]",
                DarkTheme.SYSTEM_MESSAGE
            )
