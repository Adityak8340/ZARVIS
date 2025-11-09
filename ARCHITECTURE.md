# ZARVIS Code Structure

## Overview
ZARVIS code has been refactored into a modular architecture with smaller, focused files (~150 lines each) for better maintainability and readability.

## Directory Structure

```
ZARVIS/
├── main.py                    # Main ZARVIS orchestrator (193 lines)
├── gui_main.py                # GUI entry point (42 lines)
├── requirements.txt
├── README.md
├── output/                    # Generated audio and recordings
└── src/
    ├── __init__.py
    ├── brain.py              # LLM processing (125 lines)
    ├── ear.py                # Speech-to-text (72 lines)
    ├── eye.py                # Vision processing (111 lines)
    ├── mouth.py              # Text-to-speech (65 lines)
    └── gui/                  # **NEW: Modular GUI Package**
        ├── __init__.py       # GUI entry point (24 lines)
        ├── threads.py        # Background threads (133 lines)
        ├── styles.py         # Theming and colors (87 lines)
        ├── chat_widget.py    # Chat interface (147 lines)
        ├── settings_widget.py # Settings tab (43 lines)
        ├── audio_handler.py  # Audio recording/playback (141 lines)
        └── main_window.py    # Main window coordinator (190 lines)
```

## Module Responsibilities

### Core Modules (`src/`)

#### `brain.py` (125 lines)
- LLM text processing
- Conversation memory management
- Context handling

#### `ear.py` (72 lines)
- Speech-to-text transcription
- Audio file handling via Groq Whisper

#### `eye.py` (111 lines)
- Image analysis
- Vision model integration

#### `mouth.py` (65 lines)
- Text-to-speech synthesis
- Audio file generation via Groq PlayAI

### GUI Package (`src/gui/`)

#### `__init__.py` (24 lines)
- Package entry point
- `launch_gui()` function
- Exports main classes

#### `threads.py` (133 lines)
**Purpose:** Background task execution
- `ProcessingThread` - Handles AI tasks (text, voice, vision, speech)
- `AudioRecorder` - Records audio from microphone
- Non-blocking UI operations

#### `styles.py` (87 lines)
**Purpose:** UI theming and styling
- `DarkTheme` - Dark mode stylesheet
- `Fonts` - Font configurations
- Color constants for messages

#### `chat_widget.py` (147 lines)
**Purpose:** Chat interface component
- Text input/output
- Microphone button
- Image attachment button
- Voice toggle
- Message display with color coding

#### `settings_widget.py` (43 lines)
**Purpose:** Settings tab component
- Model configuration display
- Feature list
- Clear memory button

#### `audio_handler.py` (141 lines)
**Purpose:** Audio functionality mixin
- Recording management
- Audio playback
- Speech generation
- Media player error handling

#### `main_window.py` (190 lines)
**Purpose:** Application coordinator
- Window setup and layout
- Tab management
- Event handling
- Thread lifecycle management
- Application cleanup

## Benefits of Modular Structure

### 1. **Maintainability**
- Each file has a single responsibility
- Easy to locate specific functionality
- Changes are isolated to relevant modules

### 2. **Readability**
- Files are ~43-190 lines (avg ~120 lines)
- Clear module boundaries
- Self-documenting structure

### 3. **Testability**
- Each module can be tested independently
- Mocks and stubs are easier to create
- Unit tests can target specific components

### 4. **Scalability**
- Easy to add new features
- Can replace components without affecting others
- Plugin architecture possible

### 5. **Collaboration**
- Multiple developers can work on different modules
- Reduced merge conflicts
- Clear code ownership

## Key Design Patterns

### 1. **Separation of Concerns**
- UI (widgets) separate from logic (handlers)
- Threading separate from UI
- Styling separate from functionality

### 2. **Signal-Slot Pattern**
- Qt signals for communication between components
- Loose coupling between widgets
- Event-driven architecture

### 3. **Mixin Pattern**
- `AudioHandlerMixin` adds audio functionality
- Reusable across different window types
- Clean method organization

### 4. **Thread Management**
- Background threads for all blocking operations
- Proper cleanup on application exit
- No UI freezing

## File Size Comparison

### Before Refactoring
```
src/gui.py: 608 lines  ❌ Hard to navigate
```

### After Refactoring
```
src/gui/__init__.py:        24 lines  ✓
src/gui/threads.py:        133 lines  ✓
src/gui/styles.py:          87 lines  ✓
src/gui/chat_widget.py:    147 lines  ✓
src/gui/settings_widget.py: 43 lines  ✓
src/gui/audio_handler.py:  141 lines  ✓
src/gui/main_window.py:    190 lines  ✓ (Could be split further if needed)
────────────────────────────────────────
Total:                     765 lines
```

**Result:** Increased total lines by ~26% BUT each file is now:
- Easy to understand
- Focused on one responsibility
- Quick to locate and modify

## Future Improvements

1. **Split `main_window.py` further**
   - Extract event handlers to separate file
   - Create UI builder class

2. **Add unit tests**
   - Test each module independently
   - Mock ZARVIS core for GUI tests

3. **Add type hints**
   - Full type coverage
   - Better IDE support

4. **Plugin system**
   - Custom widgets as plugins
   - Extensible architecture

## Usage

### Running the GUI
```bash
python -m gui_main
```

### Importing modules
```python
from src.gui import launch_gui
from src.gui.chat_widget import ChatWidget
from src.gui.threads import ProcessingThread
```

### Extending the GUI
```python
# Add new widget
from PyQt6.QtWidgets import QWidget
from src.gui.styles import DarkTheme

class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(DarkTheme.STYLESHEET)
```

## Conclusion

The refactored structure makes ZARVIS more professional, maintainable, and scalable while keeping individual files concise and focused.
