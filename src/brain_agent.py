"""
ZARVIS Brain Module - LangGraph Agent Orchestrator
"""
import os
from typing import TypedDict, Annotated, Sequence, Optional, Literal, Any, cast
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from src.tools.ear_tool import listen_tool
from src.tools.eye_tool import see_tool
from src.tools.mouth_tool import speak_tool


class AgentState(TypedDict):
    """State for the ZARVIS agent graph."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next: Optional[str]


class Brain:
    """
    ZARVIS Brain - LangGraph-based agent orchestrator.
    
    The Brain acts as an intelligent orchestrator that:
    1. Receives user input
    2. Decides which tools to use (Ear, Eye, Mouth)
    3. Executes tools as needed
    4. Generates final responses
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "meta-llama/llama-4-scout-17b-16e-instruct"):
        """
        Initialize the Brain orchestrator.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: LLM model to use for reasoning
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.model = model
        
        # Initialize the LLM with tool binding
        # Cast api_key to Any to avoid SecretStr type issues
        self.llm = ChatGroq(
            model=self.model,
            temperature=0.7,
            api_key=cast(Any, self.api_key)
        )
        
        # Available tools
        self.tools = [listen_tool, see_tool, speak_tool]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # System prompt
        self.system_prompt = SystemMessage(content=(
            "You are ZARVIS, a Zero-Latency Autonomous Runtime Virtual Intelligence System. "
            "You are a local, OS-integrated AI assistant that can see, hear, and speak. "
            "\n\nYou have access to these tools:"
            "\n- listen_tool: Convert audio files to text (speech-to-text)"
            "\n- see_tool: Analyze images and provide visual descriptions"
            "\n- speak_tool: Convert text to speech audio files"
            "\n\nUse these tools intelligently based on user requests. "
            "Be concise, helpful, and action-oriented. "
            "When you generate audio with speak_tool, inform the user about the file path."
        ))
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> Any:
        """Build the LangGraph StateGraph for agent orchestration."""
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Define nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def _agent_node(self, state: AgentState) -> dict[str, list[BaseMessage]]:
        """
        Agent reasoning node - decides what to do next.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with agent's response
        """
        messages = state["messages"]
        
        # Add system prompt if this is the first message
        if len(messages) == 1 or not any(isinstance(m, SystemMessage) for m in messages):
            messages = [self.system_prompt] + list(messages)
        
        # Get response from LLM
        response = self.llm_with_tools.invoke(messages)
        
        print(f"🧠 [Brain] Agent response: {response.content[:100] if response.content else 'Tool calls requested'}")
        
        return {"messages": [response]}
    
    def _should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        """
        Determine if we should continue to tools or end.
        
        Args:
            state: Current agent state
            
        Returns:
            "continue" if tools should be called, "end" otherwise
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there are tool calls, continue to tools
        if hasattr(last_message, "tool_calls") and getattr(last_message, "tool_calls", None):
            tool_calls = getattr(last_message, "tool_calls", [])
            print(f"🔧 [Brain] Routing to tools: {[tc.get('name', 'unknown') for tc in tool_calls]}")
            return "continue"
        
        # Otherwise, end
        print("✓ [Brain] Execution complete")
        return "end"
    
    def think(self, user_input: str, context: Optional[dict] = None) -> str:
        """
        Process user input through the agent graph.
        
        Args:
            user_input: User's message or query
            context: Additional context (optional)
            
        Returns:
            AI-generated response
        """
        # Build the user message
        user_message = user_input
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            user_message = f"Context:\n{context_str}\n\nUser: {user_input}"
        
        # Create initial state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=user_message)],
            "next": None
        }
        
        print(f"🧠 [Brain] Processing: {user_input[:100]}...")
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        # Extract the final response
        final_message = result["messages"][-1]
        
        if isinstance(final_message, AIMessage):
            content = final_message.content
            if isinstance(content, str):
                response = content
            elif isinstance(content, list):
                # Handle list content (extract text parts)
                response = " ".join([str(item) for item in content])
            else:
                response = str(content) if content else ""
        else:
            response = str(final_message.content) if hasattr(final_message, "content") else str(final_message)
        
        print(f"✓ [Brain] Response generated ({len(response)} chars)")
        return response
    
    def stream_think(self, user_input: str, context: Optional[dict] = None):
        """
        Stream the agent's thinking process.
        
        Args:
            user_input: User's message or query
            context: Additional context (optional)
            
        Yields:
            State updates from the graph execution
        """
        # Build the user message
        user_message = user_input
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            user_message = f"Context:\n{context_str}\n\nUser: {user_input}"
        
        # Create initial state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=user_message)],
            "next": None
        }
        
        print(f"🧠 [Brain] Streaming response for: {user_input[:100]}...")
        
        # Stream the graph execution
        for state in self.graph.stream(initial_state):
            yield state
    
    def get_conversation_history(self) -> list[BaseMessage]:
        """
        Get the conversation history.
        
        Note: In the current implementation, history is managed per invocation.
        For persistent history, you'd need to maintain state externally.
        
        Returns:
            List of messages (currently empty as state is per-call)
        """
        return []
    
    def clear_history(self):
        """Clear conversation history (placeholder for future implementation)."""
        print("✓ [Brain] History cleared (stateless mode)")


if __name__ == "__main__":
    # Test the Brain module
    brain = Brain()
    response = brain.think("Hello! What can you do?")
    print(f"\nResponse: {response}")
