"""
ZARVIS - Zero-Latency Autonomous Runtime Virtual Intelligence System
Main entry point and orchestrator using LangGraph agents and tools
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from src.brain_agent import Brain
from src.tools.ear_tool import transcribe_audio
from src.tools.eye_tool import analyze_image
from src.tools.mouth_tool import text_to_speech


class ZARVIS:
    """Main ZARVIS controller - integrates LangGraph agent orchestrator with tools."""
    
    def __init__(self):
        """Initialize ZARVIS with the Brain agent orchestrator."""
        # Load environment variables
        load_dotenv()
        
        # Verify API key is set
        if not os.environ.get("GROQ_API_KEY"):
            raise ValueError(
                "GROQ_API_KEY not found. Please set it in your .env file or environment variables."
            )
        
        print("🧠 Initializing ZARVIS with LangGraph Agent Architecture...")
        
        # Initialize the Brain agent (orchestrator)
        self.brain = Brain()
        
        print("✓ Brain agent orchestrator initialized")
        print("✓ Tools registered: Ear (listen), Eye (see), Mouth (speak)")
        print("=" * 60)
    
    def process_text_command(self, user_input: str, context: Optional[dict] = None) -> str:
        """
        Process a text command through the brain agent.
        
        Args:
            user_input: User's text input
            context: Optional context dictionary
            
        Returns:
            Response text
        """
        response = self.brain.think(user_input, context)
        return response
    
    def process_voice_command(self, audio_file: str, generate_speech: bool = True) -> str:
        """
        Process a voice command using the agent to orchestrate tools.
        The agent will automatically use listen_tool and optionally speak_tool.
        
        Args:
            audio_file: Path to audio file
            generate_speech: Whether to generate speech response
            
        Returns:
            Response text
        """
        # Let the agent handle the transcription and response
        prompt = f"Please transcribe the audio file at '{audio_file}' and respond to what was said."
        if generate_speech:
            prompt += " Also generate a speech audio file with your response."
        
        response = self.brain.think(prompt)
        return response
    
    def analyze_image(self, image_url: str, prompt: Optional[str] = None) -> str:
        """
        Analyze an image using the agent to orchestrate the vision tool.
        
        Args:
            image_url: URL of image to analyze
            prompt: Optional specific question about the image
            
        Returns:
            Analysis result
        """
        # Let the agent handle image analysis using the see_tool
        full_prompt = f"Analyze the image at '{image_url}'. "
        full_prompt += prompt or "Describe what you see in detail."
        
        response = self.brain.think(full_prompt)
        return response
    
    def multimodal_interaction(self, text: Optional[str] = None, audio: Optional[str] = None, 
                               image: Optional[str] = None) -> str:
        """
        Handle multimodal input (text, audio, and/or image) using agent orchestration.
        The agent will automatically determine which tools to use.
        
        Args:
            text: Text input
            audio: Audio file path
            image: Image URL
            
        Returns:
            Response text
        """
        # Build a comprehensive prompt for the agent
        prompt_parts = []
        
        if audio:
            prompt_parts.append(f"First, transcribe the audio file at '{audio}'.")
        
        if image:
            prompt_parts.append(f"Analyze the image at '{image}'.")
        
        if text:
            prompt_parts.append(f"User says: {text}")
        
        if not prompt_parts:
            return "No input provided."
        
        full_prompt = " ".join(prompt_parts)
        full_prompt += " Provide a comprehensive response based on all the inputs."
        
        response = self.brain.think(full_prompt)
        return response
    
    def speak_response(self, text: str) -> str:
        """
        Convert text response to speech using the agent.
        
        Args:
            text: Text to speak
            
        Returns:
            Path to audio file (or agent's response)
        """
        prompt = f"Generate a speech audio file with the following text: {text}"
        response = self.brain.think(prompt)
        return response


def main():
    """Main execution function."""
    print("=" * 60)
    print("🧠 ZARVIS - Zero-Latency Autonomous Runtime Virtual Intelligence System")
    print("=" * 60)
    
    try:
        # Initialize ZARVIS
        zarvis = ZARVIS()
        
        # Example 1: Simple text interaction
        print("\n📝 Example 1: Text Interaction")
        response = zarvis.process_text_command(
            "Hello ZARVIS! Can you introduce yourself?"
        )
        print(f"ZARVIS: {response}")
        
        # Example 2: Vision analysis
        print("\n👁️ Example 2: Vision Analysis")
        vision_result = zarvis.analyze_image(
            "https://upload.wikimedia.org/wikipedia/commons/d/da/SF_From_Marin_Highlands3.jpg",
            "What city is this and what landmarks can you see?"
        )
        print(f"Vision Analysis: {vision_result}")
        
        # Example 3: Generate speech
        print("\n🗣️ Example 3: Text-to-Speech")
        audio_file = zarvis.speak_response(
            "I am ZARVIS, your zero-latency autonomous virtual intelligence system."
        )
        print(f"Speech generated at: {audio_file}")
        
        print("\n" + "=" * 60)
        print("✓ ZARVIS demonstration complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
