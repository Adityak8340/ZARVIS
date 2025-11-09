"""
ZARVIS Brain Module - LLM-powered reasoning and decision logic using Groq
"""
import os
from groq import Groq
from typing import List, Dict, Any, Optional, cast


class Brain:
    """Handles reasoning, decision-making, and conversational intelligence."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "meta-llama/llama-4-scout-17b-16e-instruct"):
        """
        Initialize the Brain module.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: LLM model to use for reasoning
        """
        self.client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = (
            "You are ZARVIS, a Zero-Latency Autonomous Runtime Virtual Intelligence System. "
            "You are a local, OS-integrated AI assistant that can see, hear, speak, and act. "
            "You help users with tasks, automation, and information retrieval. "
            "Be concise, helpful, and action-oriented."
        )
    
    def think(self, user_input: str, context: Optional[Dict[str, Any]] = None,
              temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Process user input and generate a response.
        
        Args:
            user_input: User's message or query
            context: Additional context (vision data, system state, etc.)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            AI-generated response
        """
        # Build the message with context if provided
        user_message = user_input
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            user_message = f"Context:\n{context_str}\n\nUser: {user_input}"
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Prepare messages with system prompt
            messages: Any = [
                {"role": "system", "content": self.system_prompt}
            ] + self.conversation_history
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=cast(Any, messages),
                temperature=temperature,
                max_completion_tokens=max_tokens,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            response = completion.choices[0].message.content or ""
            
            # Add response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            print(f"✓ Brain processed input ({len(user_input)} chars) -> response ({len(response)} chars)")
            return response
        
        except Exception as e:
            print(f"✗ Error in reasoning: {e}")
            raise
    
    def decide(self, situation: str, options: List[str]) -> str:
        """
        Make a decision given a situation and options.
        
        Args:
            situation: Description of the situation
            options: List of possible actions/options
            
        Returns:
            Recommended decision with reasoning
        """
        options_str = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        prompt = (
            f"Situation: {situation}\n\n"
            f"Options:\n{options_str}\n\n"
            f"Analyze the situation and recommend the best option. Explain your reasoning."
        )
        return self.think(prompt, temperature=0.3)
    
    def clear_memory(self):
        """Clear conversation history."""
        self.conversation_history = []
        print("✓ Memory cleared")
    
    def set_system_prompt(self, prompt: str):
        """Update the system prompt."""
        self.system_prompt = prompt
        print("✓ System prompt updated")


if __name__ == "__main__":
    # Test the Brain module
    brain = Brain()
    
    response = brain.think("What can you help me with?")
    print(f"\nBrain response:\n{response}")
    
    # Test decision-making
    decision = brain.decide(
        "User wants to organize files",
        ["Sort by date", "Sort by type", "Sort by size", "Create custom folders"]
    )
    print(f"\nDecision:\n{decision}")
