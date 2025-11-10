"""
Background Threads for ZARVIS GUI
Handles AI processing and audio recording in separate threads.
"""
import tempfile
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal


class ProcessingThread(QThread):
    """Thread for running AI processing tasks without blocking UI."""
    
    finished = pyqtSignal(str)
    audio_ready = pyqtSignal(str)  # Signal for audio file path
    error = pyqtSignal(str)
    
    def __init__(self, zarvis, task_type: str, **kwargs):
        """
        Initialize processing thread.
        
        Args:
            zarvis: ZARVIS instance
            task_type: Type of task ('text', 'voice', 'vision', 'speak')
            **kwargs: Additional arguments for the task
        """
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
                # Use the tool directly for faster speech generation in GUI
                from src.tools.mouth_tool import text_to_speech
                audio_path = text_to_speech(
                    self.kwargs.get("text", ""),
                    output_filename=f"speech_{id(self)}.wav"
                )
                self.audio_ready.emit(str(audio_path))
            
        except Exception as e:
            self.error.emit(str(e))


class AudioRecorder(QThread):
    """Thread for recording audio from microphone."""
    
    recording_finished = pyqtSignal(str)  # Emits path to saved audio
    error = pyqtSignal(str)
    
    def __init__(self, duration: int = 10, sample_rate: int = 16000):
        """
        Initialize audio recorder.
        
        Args:
            duration: Maximum recording duration in seconds
            sample_rate: Audio sample rate (16kHz for speech)
        """
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
            
            # Callback to collect audio chunks
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
