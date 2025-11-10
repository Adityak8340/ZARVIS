# ZARVIS Architecture - LangGraph Agent System

## 🎯 Overview

ZARVIS (Zero-Latency Autonomous Runtime Virtual Intelligence System) is a **LangGraph-based agent orchestrator** that intelligently coordinates multimodal AI capabilities through tools. The system uses a **Brain agent** as the central orchestrator with **Ear, Eye, and Mouth** as LangGraph tools.

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         ZARVIS                              │
│                    (Main Controller)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Brain Agent                               │
│              (LangGraph Orchestrator)                       │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐       ┌──────────┐  │
│  │ Agent Node   │─────▶│ Tool Router  │─────▶│ Tools    │  │
│  │ (Reasoning)  │◀─────│ (Decision)   │◀─────│ (Execute)│  │
│  └──────────────┘      └──────────────┘       └──────────┘  │
│         │                                           │       │
│         └───────────────────┬───────────────────────┘       │
│                             │                               │
└─────────────────────────────┼───────────────────────────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
       ┌─────────────────┐      ┌─────────────────┐
       │  LangGraph Tools│      │   Tool Node     │
       └─────────────────┘      └─────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│   Ear   │  │   Eye   │  │  Mouth  │
│  Tool   │  │  Tool   │  │  Tool   │
│ (Listen)│  │  (See)  │  │ (Speak) │
└─────────┘  └─────────┘  └─────────┘
     │            │            │
     ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Groq    │  │ Groq    │  │ Groq    │
│ Whisper │  │ Vision  │  │ PlayAI  │
│  API    │  │  API    │  │  TTS    │
└─────────┘  └─────────┘  └─────────┘
```

---

## 📁 Project Structure

```
ZARVIS/
├── main.py                      # Main ZARVIS controller with agent integration
├── gui_main.py                  # GUI entry point
├── test_agent.py                # Agent testing script
├── requirements.txt             # Dependencies (includes LangGraph)
├── README.md                    # Project overview
├── ARCHITECTURE.md              # This file
├── ARCHITECTURE_LANGGRAPH.md    # Detailed LangGraph implementation
├── MIGRATION.md                 # Migration guide from old architecture
├── SUMMARY.md                   # Project summary and statistics
├── AUDIO_CLEANUP.md             # Audio cleanup feature documentation
├── output/                      # Generated audio and recordings (auto-cleaned)
└── src/
    ├── __init__.py
    ├── brain_agent.py           # 🧠 LangGraph Agent Orchestrator (NEW)
    ├── brain_old.py             # 📦 Original brain module (backup)
    ├── ear.py                   # 📦 Original ear module (backup)
    ├── eye.py                   # 📦 Original eye module (backup)
    ├── mouth.py                 # 📦 Original mouth module (backup)
    ├── tools/                   # 🔧 LangGraph Tools Package (NEW)
    │   ├── __init__.py
    │   ├── ear_tool.py          # 👂 Speech-to-Text Tool
    │   ├── eye_tool.py          # 👁️ Vision Analysis Tool
    │   └── mouth_tool.py        # 🗣️ Text-to-Speech Tool
    └── gui/                     # 💻 GUI Package
        ├── __init__.py
        ├── threads.py           # Background task threads
        ├── styles.py            # Dark theme and styling
        ├── chat_widget.py       # Chat interface component
        ├── settings_widget.py   # Settings tab component
        ├── audio_handler.py     # Audio recording/playback (with auto-cleanup)
        └── main_window.py       # Main window coordinator
```

---

## 🧠 Brain Agent (Orchestrator)

**File:** `src/brain_agent.py`

### Purpose
The Brain is a **LangGraph-based intelligent orchestrator** that:
1. Receives user input
2. Decides which tools to use (Ear, Eye, Mouth)
3. Executes tools as needed
4. Generates final responses

### Key Components

#### 1. AgentState (TypedDict)
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next: Optional[str]
```
- Manages conversation messages
- Tracks execution flow
- Uses LangChain message types

#### 2. StateGraph Architecture
```python
workflow = StateGraph(AgentState)
workflow.add_node("agent", self._agent_node)      # Reasoning
workflow.add_node("tools", ToolNode(self.tools))  # Tool execution
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", self._should_continue, {...})
workflow.add_edge("tools", "agent")
```

#### 3. Execution Flow
```
User Input → Agent Node → Decision
                ↓
         [Tool Call Needed?]
           ↙         ↘
         Yes          No
          ↓            ↓
      Tool Node    Response
          ↓
     Agent Node → Final Response
```

### Methods

| Method | Purpose |
|--------|---------|
| `think(user_input, context)` | Process input through agent graph |
| `stream_think(user_input, context)` | Stream agent's reasoning process |
| `_agent_node(state)` | LLM reasoning with tool binding |
| `_should_continue(state)` | Routing logic for tool calls |

### System Prompt
```
You are ZARVIS, a Zero-Latency Autonomous Runtime Virtual Intelligence System.
You are a local, OS-integrated AI assistant that can see, hear, and speak.

You have access to these tools:
- listen_tool: Convert audio files to text (speech-to-text)
- see_tool: Analyze images and provide visual descriptions
- speak_tool: Convert text to speech audio files

Use these tools intelligently based on user requests.
Be concise, helpful, and action-oriented.
```

---

## 🔧 Tools Package

### 1. Ear Tool (`src/tools/ear_tool.py`)

**Purpose:** Speech-to-Text conversion

```python
@tool
def listen_tool(audio_file_path: str, prompt: str = "Transcribe clearly") -> str:
    """
    Transcribe audio file to text using Groq Whisper.
    
    Use this tool when you need to convert speech/audio to text.
    """
    # Uses Groq Whisper Large V3
    # Returns transcribed text
```

**Capabilities:**
- Supports multiple audio formats (WAV, MP3, M4A, etc.)
- Context-aware transcription with prompt guidance
- Fast processing via Groq API
- Error handling and logging

**Usage:**
```python
# Agent automatically uses when it detects audio processing need
result = brain.think("Transcribe the audio at 'recording.m4a'")
```

---

### 2. Eye Tool (`src/tools/eye_tool.py`)

**Purpose:** Vision and Image Analysis

```python
@tool
def see_tool(image_url: str, prompt: str = "Describe what you see...") -> str:
    """
    Analyze an image and provide detailed observations using vision AI.
    
    Use this tool when you need to understand visual content.
    """
    # Uses Groq Vision (Llama 4 Scout)
    # Returns detailed image analysis
```

**Capabilities:**
- Analyzes images from URLs
- Identifies objects, text, scenes
- Provides detailed descriptions
- Understands visual context

**Usage:**
```python
# Agent automatically uses when it detects image analysis need
result = brain.think("What's in the image at 'https://example.com/photo.jpg'?")
```

---

### 3. Mouth Tool (`src/tools/mouth_tool.py`)

**Purpose:** Text-to-Speech synthesis

```python
@tool
def speak_tool(text: str, output_filename: str = "speech.wav", 
               voice: str = "Aaliyah-PlayAI") -> str:
    """
    Convert text to speech and save as an audio file.
    
    Use this tool when you need to generate speech audio.
    """
    # Uses Groq PlayAI TTS
    # Returns path to generated audio file
```

**Capabilities:**
- Generates natural speech from text
- Creates WAV audio files
- Customizable voice selection
- Saves to output directory

**Usage:**
```python
# Agent automatically uses when speech generation is needed
result = brain.think("Generate audio saying 'Hello World'")
```

---

## 💻 GUI System

### Architecture
The GUI uses PyQt6 with a modular design pattern:

```
Main Window (Coordinator)
    ├── Chat Widget (User Interface)
    ├── Settings Widget (Configuration)
    ├── Audio Handler Mixin (Voice I/O)
    ├── Processing Threads (Background Tasks)
    └── Media Player (Audio Playback)
```

### Key Components

#### 1. Main Window (`src/gui/main_window.py`)
- Application coordinator
- Window setup and layout
- Tab management
- Event handling
- Thread lifecycle management

#### 2. Chat Widget (`src/gui/chat_widget.py`)
- Text input/output
- Microphone button
- Image attachment button
- Voice toggle
- Message display with color coding

#### 3. Audio Handler (`src/gui/audio_handler.py`)
- Recording management
- Audio playback
- Speech generation
- **Automatic file cleanup** 🧹

#### 4. Processing Threads (`src/gui/threads.py`)
- `ProcessingThread` - AI tasks (text, voice, vision, speech)
- `AudioRecorder` - Microphone recording
- Non-blocking UI operations

#### 5. Styles (`src/gui/styles.py`)
- Dark theme stylesheet
- Color constants
- Font configurations

---

## 🧹 Audio Cleanup Feature

**Implemented in:** `src/gui/audio_handler.py`

### Purpose
Automatically delete temporary audio files during runtime to prevent disk space buildup.

### What Gets Cleaned Up

1. **Generated Speech Files** (from text-to-speech)
   - Deleted 200ms after playback completes
   - Example: `speech_123456.wav`

2. **Recorded Voice Files** (from microphone)
   - Deleted 500ms after transcription completes
   - Example: `recording_1699567890000.wav`

### How It Works

#### For Generated Speech:
```
User Message → Agent Response → speak_tool creates audio 
→ Audio plays → Playback ends → 200ms delay → File deleted ✓
```

#### For Voice Recordings:
```
User records → File saved → Transcribed by agent → Response shown 
→ 500ms delay → Recording deleted ✓
```

### Implementation
```python
def _cleanup_audio_file(self):
    """Delete the current audio file after playback."""
    if hasattr(self, 'current_audio_file') and self.current_audio_file:
        audio_path = Path(self.current_audio_file)
        if audio_path.exists():
            time.sleep(0.1)  # Ensure file is released
            audio_path.unlink()
            print(f"✓ Cleaned up audio file: {audio_path.name}")
```

---

## 🔄 Interaction Flows

### Text Command
```
1. User types message
2. ZARVIS.process_text_command()
3. Brain Agent processes
4. Agent Node reasons
5. Direct response (no tools)
6. Response displayed
```

### Voice Command
```
1. User clicks microphone
2. AudioRecorder records
3. Audio saved to output/
4. ZARVIS.process_voice_command()
5. Brain Agent receives prompt
6. Agent uses listen_tool
7. Tool Node transcribes
8. Agent processes text
9. Response generated
10. Recording deleted ✓
```

### Image Analysis
```
1. User attaches image
2. ZARVIS.analyze_image()
3. Brain Agent receives prompt with URL
4. Agent uses see_tool
5. Tool Node analyzes image
6. Agent synthesizes insights
7. Analysis returned
```

### Voice Response
```
1. Agent generates text response
2. Voice enabled check
3. GUI triggers speak_tool
4. Audio file created
5. Media player plays
6. Playback completes
7. Audio file deleted ✓
```

---

## 🎯 Key Benefits of LangGraph Architecture

### 1. **Intelligent Orchestration**
- Agent automatically decides which tools to use
- No manual routing logic needed
- Dynamic tool selection based on context

### 2. **Scalability**
- Easy to add new tools (just use `@tool` decorator)
- Tools are self-contained modules
- Agent learns new capabilities automatically

### 3. **Maintainability**
- Clear separation of concerns
- Tools are independently testable
- Agent logic is centralized

### 4. **Flexibility**
- Support for complex workflows
- Streaming responses
- Conditional tool execution

### 5. **Observability**
- Full message history in state
- Observable tool calls
- Debug-friendly architecture

### Console Output Example:
```
🧠 [Brain] Processing: Analyze this image...
🔧 [Brain] Routing to tools: ['see_tool']
👁️ [Eye Tool] Analyzed image, returned 250 characters
✓ [Brain] Execution complete
✓ Cleaned up audio file: speech_123456.wav
```

---

## 📦 Dependencies

### Core
```txt
groq==0.33.0                    # Groq API for LLM, Vision, TTS, STT
python-dotenv==1.2.1            # Environment variables
```

### LangGraph & LangChain
```txt
langgraph==1.0.2                # Agent orchestration framework
langchain-core==0.3.22          # Core abstractions
langchain-groq==1.0.0           # Groq integration
langchain==1.0.5                # Full library
```

### GUI
```txt
PyQt6==6.10.0                   # Desktop interface
pillow==12.0.0                  # Image processing
sounddevice==0.5.3              # Audio recording
soundfile==0.13.1               # Audio file handling
```

---

## 🚀 Usage Examples

### 1. Basic Text Interaction
```python
from main import ZARVIS

zarvis = ZARVIS()
response = zarvis.process_text_command("Hello ZARVIS!")
print(response)
```

### 2. Voice Command Processing
```python
zarvis = ZARVIS()
response = zarvis.process_voice_command(
    "recording.m4a",
    generate_speech=True
)
print(response)
```

### 3. Image Analysis
```python
zarvis = ZARVIS()
result = zarvis.analyze_image(
    "https://example.com/image.jpg",
    "What objects do you see?"
)
print(result)
```

### 4. Multimodal Interaction
```python
zarvis = ZARVIS()
response = zarvis.multimodal_interaction(
    text="Analyze both inputs",
    audio="voice.m4a",
    image="https://example.com/photo.jpg"
)
print(response)
```

### 5. Direct Agent Access
```python
from src.brain_agent import Brain

brain = Brain()

# Natural language - agent decides everything!
response = brain.think(
    "Listen to audio.m4a, analyze image.jpg, "
    "and create a speech response"
)
print(response)
```

---

## 🔧 Adding New Tools

### Step 1: Create Tool
```python
# src/tools/my_tool.py
from langchain_core.tools import tool

@tool
def my_new_tool(param: str) -> str:
    """
    Description of what this tool does.
    The agent will read this to understand when to use it.
    """
    # Implementation
    return result
```

### Step 2: Register in Brain
```python
# src/brain_agent.py
from src.tools.my_tool import my_new_tool

# In __init__:
self.tools = [listen_tool, see_tool, speak_tool, my_new_tool]
```

### Step 3: Done!
The agent will automatically learn to use your new tool based on its docstring!

---

## 🎓 Technical Details

### LangGraph Flow
```
┌─────────────────────┐
│   User Input        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Agent Node        │
│   (Reasoning)       │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │  Tool Call?  │
    └──────┬───────┘
           │
    ┌──────┴──────┐
    │             │
   Yes           No
    │             │
    ▼             ▼
┌─────────┐   ┌─────────┐
│  Tools  │   │  END    │
│  Node   │   └─────────┘
└────┬────┘
     │
     ▼
┌─────────────┐
│ Agent Node  │
│ (Synthesis) │
└──────┬──────┘
       │
       ▼
   ┌─────────┐
   │  END    │
   └─────────┘
```

### Message Types
- `HumanMessage` - User input
- `AIMessage` - Agent responses
- `SystemMessage` - System prompts
- `ToolMessage` - Tool execution results

### State Management
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next: Optional[str]
```

---

## 📊 Performance Characteristics

### Latency
- **LLM Response:** ~1-2 seconds (Groq optimized)
- **Speech-to-Text:** ~0.5-1 second
- **Text-to-Speech:** ~1-2 seconds
- **Vision Analysis:** ~1-2 seconds

### Resource Usage
- **Memory:** ~200-500 MB (depending on GUI)
- **CPU:** Minimal (API-based processing)
- **Disk:** Auto-cleanup keeps it minimal
- **Network:** Requires internet for Groq API

---

## 🔒 Security & Privacy

### API Key Management
- Stored in `.env` file (not committed to git)
- Loaded via `python-dotenv`
- Never exposed in logs

### File Cleanup
- Automatic deletion of temporary audio files
- No persistent storage of voice recordings
- Output directory kept clean

### Tool Safety
- Tools have clear permissions and descriptions
- Agent can only use registered tools
- No arbitrary code execution

---

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
```bash
pip install --upgrade langgraph langchain-core langchain-groq
```

2. **API Key Missing**
```bash
# Check .env file
GROQ_API_KEY=your_key_here
```

3. **Audio Playback Issues**
- Check file permissions in `output/` directory
- Ensure media player has access to files
- Check console for cleanup logs

4. **Tool Not Being Called**
- Check tool is registered in `brain_agent.py`
- Verify tool docstring is clear
- Check console for routing decisions

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `ARCHITECTURE.md` | This file - Complete system architecture |
| `ARCHITECTURE_LANGGRAPH.md` | Detailed LangGraph implementation guide |
| `MIGRATION.md` | Migration guide from old architecture |
| `SUMMARY.md` | Project statistics and overview |
| `AUDIO_CLEANUP.md` | Audio cleanup feature documentation |
| `README.md` | Quick start and project overview |

---

## 🔮 Future Enhancements

### Planned Features

1. **Persistent Memory**
   - Conversation history across sessions
   - User preferences and context
   - Checkpointing for long conversations

2. **Advanced Tool Composition**
   - Sequential tool chains
   - Parallel tool execution
   - Tool result aggregation

3. **Custom Nodes**
   - Decision-making nodes
   - Validation nodes
   - Post-processing nodes

4. **Enhanced Error Handling**
   - Retry logic for failed tools
   - Fallback strategies
   - Graceful degradation

5. **Performance Optimization**
   - Caching tool results
   - Lazy tool loading
   - Batch processing

---

## 📝 Version History

### v2.0.0 - LangGraph Refactoring (Current)
- ✅ Migrated to LangGraph architecture
- ✅ Brain as agent orchestrator
- ✅ Ear, Eye, Mouth as tools
- ✅ Intelligent tool selection
- ✅ Automatic audio cleanup
- ✅ Comprehensive documentation

### v1.0.0 - Original Architecture
- Basic module structure
- Direct function calls
- Manual orchestration
- Manual file management

---

## 🤝 Contributing

When adding new features:
1. Create tools with `@tool` decorator
2. Add clear docstrings (agent reads these!)
3. Test tools independently
4. Update documentation
5. Submit PR with examples

---

## 📞 Support

For questions or issues:
1. Check this documentation
2. Review `ARCHITECTURE_LANGGRAPH.md` for implementation details
3. Check `MIGRATION.md` for usage examples
4. Look at console logs for debugging

---

**ZARVIS v2.0 - Zero-Latency Autonomous Runtime Virtual Intelligence System**

**Built with ❤️ using LangGraph, LangChain, and Groq**
