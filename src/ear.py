"""
ZARVIS Ear Module - Speech-to-Text using Groq Whisper
"""
import os
from pathlib import Path
from typing import Optional
from groq import Groq


class Ear:
    """Handles speech recognition and audio transcription using Groq Whisper."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "whisper-large-v3"):
        """
        Initialize the Ear module.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Whisper model to use for transcription
        """
        self.client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
        self.model = model
    
    def listen(self, audio_file_path: str, 
               prompt: str = "Specify context or spelling") -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to the audio file
            prompt: Optional context or spelling guidance
            
        Returns:
            Transcribed text
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            with open(audio_file_path, "rb") as file:
                translation = self.client.audio.translations.create(
                    file=(audio_file_path, file.read()),
                    model=self.model,
                    prompt=prompt,
                    response_format="json",
                    temperature=0.0
                )
                
                print(f"✓ Transcription completed: {len(translation.text)} characters")
                return translation.text
        
        except Exception as e:
            print(f"✗ Error transcribing audio: {e}")
            raise
    
    def transcribe(self, audio_file_path: str, prompt: Optional[str] = None) -> str:
        """
        Alternative method name for transcription.
        
        Args:
            audio_file_path: Path to the audio file
            prompt: Optional context or spelling guidance
            
        Returns:
            Transcribed text
        """
        return self.listen(audio_file_path, prompt=prompt or "Transcribe clearly")


if __name__ == "__main__":
    # Test the Ear module
    ear = Ear()
    # Replace with actual audio file path for testing
    # text = ear.listen("path/to/audio.m4a")
    # print(f"Transcribed: {text}")
    print("Ear module initialized. Provide an audio file path to test.")
