"""
ZARVIS - Zero-Latency Autonomous Runtime Virtual Intelligence System
Main entry point and orchestrator
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from src.mouth import Mouth
from src.ear import Ear
from src.eye import Eye
from src.brain import Brain


class ZARVIS:
    """Main ZARVIS controller - integrates all modules."""
    
    def __init__(self):
        """Initialize ZARVIS with all cognitive modules."""
        # Load environment variables
        load_dotenv()
        
        # Verify API key is set
        if not os.environ.get("GROQ_API_KEY"):
            raise ValueError(
                "GROQ_API_KEY not found. Please set it in your .env file or environment variables."
            )
        
        print("🧠 Initializing ZARVIS...")
        
        # Initialize modules
        self.mouth = Mouth()
        self.ear = Ear()
        self.eye = Eye()
        self.brain = Brain()
        
        print("✓ All modules initialized successfully")
        print("=" * 60)
    
    def process_text_command(self, user_input: str, context: Optional[dict] = None) -> str:
        """
        Process a text command through the brain.
        
        Args:
            user_input: User's text input
            context: Optional context dictionary
            
        Returns:
            Response text
        """
        response = self.brain.think(user_input, context)
        return response
    
    def process_voice_command(self, audio_file: str) -> str:
        """
        Process a voice command (audio -> text -> brain -> text -> audio).
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Response text
        """
        # Listen (speech to text)
        print("👂 Listening...")
        user_input = self.ear.listen(audio_file)
        print(f"Heard: {user_input}")
        
        # Think (process through brain)
        print("🧠 Thinking...")
        response = self.brain.think(user_input)
        print(f"Response: {response}")
        
        # Speak (text to speech)
        print("🗣️ Speaking...")
        audio_path = self.mouth.speak(response)
        print(f"Audio saved: {audio_path}")
        
        return response
    
    def analyze_image(self, image_url: str, prompt: Optional[str] = None) -> str:
        """
        Analyze an image and provide insights.
        
        Args:
            image_url: URL of image to analyze
            prompt: Optional specific question about the image
            
        Returns:
            Analysis result
        """
        print("👁️ Analyzing image...")
        result = self.eye.see(
            image_url, 
            prompt=prompt or "Describe what you see in detail."
        )
        return result
    
    def multimodal_interaction(self, text: Optional[str] = None, audio: Optional[str] = None, 
                               image: Optional[str] = None) -> str:
        """
        Handle multimodal input (text, audio, and/or image).
        
        Args:
            text: Text input
            audio: Audio file path
            image: Image URL
            
        Returns:
            Response text
        """
        context = {}
        
        # Process audio if provided
        if audio:
            print("👂 Processing audio input...")
            text = self.ear.listen(audio)
            context["audio_input"] = text
        
        # Process image if provided
        if image:
            print("👁️ Processing visual input...")
            vision_result = self.eye.see(image, "Describe what you see.")
            context["vision_input"] = vision_result
        
        # Process through brain with context
        if text:
            print("🧠 Processing with context...")
            response = self.brain.think(text, context)
            return response
        
        return "No input provided."
    
    def speak_response(self, text: str) -> Path:
        """
        Convert text response to speech.
        
        Args:
            text: Text to speak
            
        Returns:
            Path to audio file
        """
        return self.mouth.speak(text)


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
