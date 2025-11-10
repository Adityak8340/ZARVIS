"""
ZARVIS Eye Tool - Vision and Image Analysis as a LangGraph tool
"""
import os
from typing import Optional, Any, cast
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
def see_tool(image_url: str, prompt: str = "Describe what you see in this image in detail.") -> str:
    """
    Analyze an image and provide detailed observations using vision AI.
    
    Use this tool when you need to understand visual content, analyze images,
    identify objects, read text from images, or get descriptions of visual scenes.
    
    Args:
        image_url: URL of the image to analyze (must be a valid http/https URL or data URI)
        prompt: Specific question or instruction for image analysis
        
    Returns:
        Detailed analysis and description of the image content
    """
    try:
        client = _get_groq_client()
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
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=cast(Any, messages),
            temperature=1.0,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        result = completion.choices[0].message.content or ""
        print(f"✓ [Eye Tool] Analyzed image, returned {len(result)} characters")
        return result
    
    except Exception as e:
        error_msg = f"Error analyzing image: {str(e)}"
        print(f"✗ [Eye Tool] {error_msg}")
        return error_msg


def analyze_image(image_url: str, prompt: Optional[str] = None) -> str:
    """
    Non-decorator version for direct calling.
    
    Args:
        image_url: URL of the image to analyze
        prompt: Optional specific question about the image
        
    Returns:
        Image analysis result
    """
    return see_tool.invoke({
        "image_url": image_url,
        "prompt": prompt or "Describe what you see in this image in detail."
    })
