"""
ZARVIS Mouth Tool - Text-to-Speech as a LangGraph tool
"""
import os
from pathlib import Path
from typing import Optional
from langchain_core.tools import tool
from groq import Groq


# Initialize Groq client and output directory
_groq_client = None
_output_dir = Path(__file__).parent.parent.parent / "output"
_output_dir.mkdir(exist_ok=True)

def _get_groq_client():
    """Lazy initialization of Groq client."""
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _groq_client


@tool
def speak_tool(text: str, output_filename: str = "speech.wav", voice: str = "Aaliyah-PlayAI") -> str:
    """
    Convert text to speech and save as an audio file.
    
    Use this tool when you need to generate speech audio from text,
    create voice responses, or produce audio output for the user.
    
    Args:
        text: The text to convert to speech (cannot be empty)
        output_filename: Name for the output audio file (default: speech.wav)
        voice: Voice model to use for synthesis (default: Aaliyah-PlayAI)
        
    Returns:
        Path to the generated audio file, or error message if failed
    """
    if not text or not text.strip():
        return "Error: Text input cannot be empty"
    
    speech_file_path = _output_dir / output_filename
    
    try:
        client = _get_groq_client()
        response = client.audio.speech.create(
            model="playai-tts",
            voice=voice,
            response_format="wav",
            input=text,
        )
        
        # Write the response content to file
        with open(speech_file_path, 'wb') as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
        
        result = str(speech_file_path)
        print(f"✓ [Mouth Tool] Generated speech: {result}")
        return result
    
    except Exception as e:
        error_msg = f"Error generating speech: {str(e)}"
        print(f"✗ [Mouth Tool] {error_msg}")
        return error_msg


def text_to_speech(text: str, output_filename: str = "speech.wav", voice: str = "Aaliyah-PlayAI") -> str:
    """
    Non-decorator version for direct calling.
    
    Args:
        text: Text to convert to speech
        output_filename: Name of the output audio file
        voice: Voice model to use
        
    Returns:
        Path to generated audio file
    """
    return speak_tool.invoke({
        "text": text,
        "output_filename": output_filename,
        "voice": voice
    })
