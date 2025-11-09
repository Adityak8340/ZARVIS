"""
ZARVIS Eye Module - Vision and Image Analysis using Groq Vision
"""
import os
from groq import Groq
from typing import Dict, Any, Optional, cast


class Eye:
    """Handles vision and image analysis using Groq's vision-capable models."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "meta-llama/llama-4-scout-17b-16e-instruct"):
        """
        Initialize the Eye module.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Vision model to use for image analysis
        """
        self.client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
        self.model = model
    
    def see(self, image_url: str, prompt: str = "Describe what you see in this image in detail.",
            json_mode: bool = False, temperature: float = 1.0) -> str:
        """
        Analyze an image and return observations.
        
        Args:
            image_url: URL of the image to analyze
            prompt: Question or instruction for image analysis
            json_mode: Whether to return response in JSON format
            temperature: Sampling temperature (0.0 to 2.0)
            
        Returns:
            Analysis result as text or JSON
        """
        try:
            messages: Any = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
            
            # Build kwargs for API call
            kwargs: Dict[str, Any] = {
                "model": self.model,
                "messages": cast(Any, messages),
                "temperature": temperature,
                "max_completion_tokens": 1024,
                "top_p": 1,
                "stream": False,
                "stop": None,
            }
            
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            completion = self.client.chat.completions.create(**kwargs)
            
            result = completion.choices[0].message.content or ""
            print("✓ Vision analysis completed")
            return result
        
        except Exception as e:
            print(f"✗ Error analyzing image: {e}")
            raise
    
    def observe_screen(self, screenshot_url: str, 
                       task: str = "Analyze the screen and describe what applications and content are visible.") -> str:
        """
        Analyze a screenshot to understand on-screen context.
        
        Args:
            screenshot_url: URL of the screenshot
            task: Specific task or question about the screenshot
            
        Returns:
            Screen analysis result
        """
        return self.see(screenshot_url, prompt=task, json_mode=False)
    
    def detect_elements(self, image_url: str, 
                       elements_to_find: str = "UI elements, buttons, text, and interactive components") -> Dict[str, Any]:
        """
        Detect specific elements in an image.
        
        Args:
            image_url: URL of the image
            elements_to_find: Description of elements to detect
            
        Returns:
            Dictionary of detected elements
        """
        import json
        prompt = f"List all {elements_to_find} visible in this image. Return as JSON."
        result = self.see(image_url, prompt=prompt, json_mode=True)
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"raw_response": result}
