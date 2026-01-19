# Technology Stack

**Analysis Date:** 2026-01-19

## Languages

**Primary:**
- Python 3.x - All application code

**Secondary:**
- JSON - Data storage format for characters, scenes, mappings
- Markdown - Episode scripts and documentation

## Runtime

**Environment:**
- Python 3.x (likely 3.8+)
- Windows/Linux/macOS (cross-platform desktop application)

**Package Manager:**
- pip
- Lockfile: Not detected (requirements.txt only)

## Frameworks

**Core:**
- tkinter - GUI framework (Python built-in)
- tkinterdnd2 - Drag and drop support (optional)

**API Server:**
- Flask 2.3.0+ - ComfyUI API server (`comfyui_api_server.py`)
- flask-cors 4.0.0+ - CORS support

**Build/Dev:**
- Not applicable (interpreted Python)

## Key Dependencies

**Critical:**
- google-generativeai - Gemini AI integration (`services/llm_service.py`)
- openai - OpenAI API integration (optional)
- anthropic - Anthropic API integration (optional)
- flask - REST API server for ComfyUI integration

**Infrastructure:**
- pathlib - Path handling (Python built-in)
- argparse - Command-line argument parsing (Python built-in)
- json - JSON data handling (Python built-in)
- tkinter - GUI components (Python built-in)

## Configuration

**Environment:**
- Configuration via `config/config_manager.py`
- API keys stored in config (provider, api_key, model)
- Project paths specified via command-line: `--prompts`, `--project`

**Build:**
- No build configuration (interpreted language)
- TensorFlow environment variables set to suppress warnings

## Platform Requirements

**Development:**
- Python 3.x installation
- Optional: tkinterdnd2 for drag-and-drop
- Optional: LLM provider packages (google-generativeai, openai, anthropic)

**Production:**
- Desktop application (not web-based)
- Runs locally on user's machine
- Requires API keys for LLM providers

---

*Stack analysis: 2026-01-19*
*Update after major dependency changes*
