"""
ZARVIS Ear Tool - Speech-to-Text as a LangGraph tool
"""
import os
from typing import Optional
from langchain_core.tools import tool
from groq import Groq


# Initialize Groq client
_groq_client = None

def _get_groq_client():
    """Lazy initialization of Groq client."""
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _groq_client


@tool
def listen_tool(audio_file_path: str, prompt: str = "Transcribe clearly") -> str:
    """
    Transcribe audio file to text using Groq Whisper.
    
    Use this tool when you need to convert speech/audio to text.
    This is useful for processing voice commands, audio messages, or any audio input.
    
    Args:
        audio_file_path: Path to the audio file (supports various formats like m4a, wav, mp3)
        prompt: Optional context or spelling guidance for better transcription
        
    Returns:
        The transcribed text from the audio file
    """
    if not os.path.exists(audio_file_path):
        return f"Error: Audio file not found at {audio_file_path}"
    
    try:
        client = _get_groq_client()
        with open(audio_file_path, "rb") as file:
            translation = client.audio.translations.create(
                file=(audio_file_path, file.read()),
                model="whisper-large-v3",
                prompt=prompt,
                response_format="json",
                temperature=0.0
            )
            
            result = translation.text
            print(f"✓ [Ear Tool] Transcribed {len(result)} characters from audio")
            return result
    
    except Exception as e:
        error_msg = f"Error transcribing audio: {str(e)}"
        print(f"✗ [Ear Tool] {error_msg}")
        return error_msg


def transcribe_audio(audio_file_path: str, prompt: Optional[str] = None) -> str:
    """
    Non-decorator version for direct calling.
    
    Args:
        audio_file_path: Path to the audio file
        prompt: Optional context or spelling guidance
        
    Returns:
        Transcribed text
    """
    return listen_tool.invoke({"audio_file_path": audio_file_path, "prompt": prompt or "Transcribe clearly"})
