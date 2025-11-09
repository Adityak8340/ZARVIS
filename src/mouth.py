"""
ZARVIS Mouth Module - Text-to-Speech using Groq PlayAI TTS
"""
import os
from pathlib import Path
from typing import Optional
from groq import Groq


class Mouth:
    """Handles text-to-speech output using Groq's PlayAI TTS."""
    
    def __init__(self, api_key: Optional[str] = None, voice: str = "Aaliyah-PlayAI"):
        """
        Initialize the Mouth module.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            voice: Voice model to use for speech synthesis
        """
        self.client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
        self.voice = voice
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
    
    def speak(self, text: str, output_filename: str = "speech.wav") -> Path:
        """
        Convert text to speech and save to file.
        
        Args:
            text: Text to convert to speech
            output_filename: Name of the output audio file
            
        Returns:
            Path to the generated audio file
        """
        if not text:
            raise ValueError("Text input cannot be empty")
        
        speech_file_path = self.output_dir / output_filename
        
        try:
            response = self.client.audio.speech.create(
                model="playai-tts",
                voice=self.voice,
                response_format="wav",
                input=text,
            )
            # Write the response content to file
            with open(speech_file_path, 'wb') as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
            print(f"✓ Speech generated: {speech_file_path}")
            return speech_file_path
        
        except Exception as e:
            print(f"✗ Error generating speech: {e}")
            raise
    
    def set_voice(self, voice: str):
        """Change the voice model."""
        self.voice = voice
        print(f"✓ Voice changed to: {voice}")


if __name__ == "__main__":
    # Test the Mouth module
    mouth = Mouth()
    mouth.speak("Hello, I am ZARVIS. Your zero-latency autonomous runtime virtual intelligence system.")
