# 🧠 ZARVIS — Zero-Latency Autonomous Runtime Virtual Intelligence System

ZARVIS is a **local, OS-integrated AI assistant** that can **see, hear, speak, and act**.
It's not a chatbot — it's a **runtime intelligence layer** that perceives your environment, understands context, and executes tasks directly on your system.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green)](https://www.riverbankcomputing.com/software/pyqt/)
[![Groq](https://img.shields.io/badge/Powered%20by-Groq-orange)](https://groq.com/)

---

## 🚀 Quick Start

### Installation

**Windows (PowerShell):**
```powershell
.\setup.ps1
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Configuration

1. Get your Groq API key from [console.groq.com](https://console.groq.com/)
2. Add it to `.env`:
```
GROQ_API_KEY=your_api_key_here
```

### Run

**With GUI (Recommended):**
```bash
python gui_main.py
```

**Command Line:**
```bash
python main.py
```

---

## ⚙️ Core Features

### 🗣️ Voice

* Natural voice interaction (speech-to-text + text-to-speech)
* Always-on or push-to-talk listening
* Personalized voice responses

### 👂 Ear

* Real-time speech recognition
* Wake-word detection (“Hey Zarvis”)
* Context-aware command parsing

### 👁️ Vision

* Screen awareness through OCR and image analysis
* Detects text, windows, and visual elements
* Understands on-screen context for decision-making

### 🧠 Brain

* LLM-powered reasoning and decision logic
* Short- and long-term memory (context retention)
* Adaptive responses and behavior based on history

### ⚡ Action Engine

* Executes OS commands and automations
* Controls files, apps, and processes
* Integrates with plugins for extended capabilities

### 🔌 Plugins

* Modular skill system with manifest-based permissions
* Loadable extensions for specific domains (e.g., Git, browser, monitoring)

---

## 🧩 Architecture

* **Frontend:** PyQt6 desktop interface with dark theme
* **Core:** Python runtime for logic, AI, and memory
* **Input Systems:** Voice + Vision modules
* **Output Systems:** Speech + GUI responses
* **Action Layer:** Secure OS control and automation
* **API:** Groq for LLM, Vision, TTS, and STT

### Module Structure

```
ZARVIS/
├── main.py              # CLI entry point
├── gui_main.py          # GUI entry point
├── src/
│   ├── brain.py         # LLM reasoning (Llama 4 Scout)
│   ├── eye.py           # Vision analysis (Llama Vision)
│   ├── ear.py           # Speech-to-text (Whisper)
│   ├── mouth.py         # Text-to-speech (PlayAI)
│   └── gui/             # 📦 Modular PyQt6 interface
│       ├── __init__.py         # Package entry point
│       ├── threads.py          # Background processing
│       ├── styles.py           # UI theming
│       ├── chat_widget.py      # Chat interface
│       ├── settings_widget.py  # Settings tab
│       ├── audio_handler.py    # Voice recording/playback
│       └── main_window.py      # Main coordinator
├── output/              # Generated audio files
├── ARCHITECTURE.md      # 📖 Detailed code structure docs
└── .env                 # API configuration
```

**✨ New: Modular Architecture!**
- Each GUI file is ~43-147 lines (easy to read and maintain)
- Clear separation of concerns
- Easy to extend with new features
- See [ARCHITECTURE.md](ARCHITECTURE.md) for details

---

## 🖥️ GUI Features

- **💬 Unified Chat Interface**: 
  - Text, voice, and vision all in one place
  - 🎤 Microphone button for live voice recording
  - �️ Image button for vision analysis
  - 🗣️ Toggle for automatic voice responses
- **⚙️ Settings Tab**: Model info and memory management
- **Dark Theme**: Professional, eye-friendly interface
- **Multi-threaded**: Non-blocking UI during AI processing
- **Modular Code**: Clean architecture with focused components

---

## 📋 Requirements

- Python 3.8+
- Groq API key (free at [console.groq.com](https://console.groq.com/))
- Windows/Linux/Mac
- 2GB RAM minimum

---

## 🧠 Philosophy

ZARVIS isn't built to chat — it's built to **think, perceive, and act locally**.
It merges **voice, vision, and reasoning** to create an intelligent, autonomous assistant that operates directly within your system environment.

> "Not just an assistant — your OS's second brain."

---

## 📚 Documentation

- [GUI Guide](README_GUI.md) - Detailed GUI usage instructions
- [API Documentation](https://console.groq.com/docs) - Groq API reference

---

## 🛠️ Development

### Adding New Features

Each cognitive module is independent and can be extended:

```python
from src.brain import Brain
from src.eye import Eye

brain = Brain()
eye = Eye()

# Multimodal interaction
vision_data = eye.see("image_url.jpg")
response = brain.think("Analyze this", context={"vision": vision_data})
```

### Running Tests

```bash
python -m pytest tests/
```

---

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines and submit PRs.

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Powered by [Groq](https://groq.com/) for ultra-fast AI inference
- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the GUI
- Models: Llama 4 Scout, Whisper v3, PlayAI TTS
