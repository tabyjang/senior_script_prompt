# Codebase Structure

**Analysis Date:** 2026-01-19

## Directory Layout

```
script_editors_app/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── config/                     # Configuration management
│   ├── __init__.py
│   └── config_manager.py
├── models/                     # Data models
│   ├── __init__.py
│   ├── project_data.py
│   └── piper/                  # TTS model files (optional)
├── services/                   # Business logic services
│   ├── __init__.py
│   ├── llm_service.py
│   ├── file_service.py
│   ├── content_generator.py
│   ├── comfyui_service.py
│   └── google_sheets_service.py
├── gui/                        # User interface
│   ├── __init__.py
│   ├── main_window.py
│   ├── tabs/                   # Feature tabs
│   │   ├── base_tab.py
│   │   ├── synopsis_input_tab.py
│   │   ├── characters_tab.py
│   │   ├── chapters_tab.py
│   │   ├── scripts_tab.py
│   │   ├── scenes_tab.py
│   │   ├── image_prompts_input_tab.py
│   │   ├── image_generation_tab.py
│   │   ├── comfyui_tab.py
│   │   ├── word_converter_tab.py
│   │   ├── tts_tab.py
│   │   └── episode_splitter_tab.py
│   └── dialogs/
│       ├── __init__.py
│       └── settings_dialog.py
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── json_utils.py
│   ├── ui_helpers.py
│   ├── file_utils.py
│   └── word_converter.py
├── prompts/                    # Project data storage
│   └── {project_name}/
│       ├── characters/
│       ├── scenes/
│       ├── mappings/
│       └── *_episodes/
├── output/                     # Generated outputs
│   └── tts/                    # TTS audio files
├── comfyui_api_server.py      # ComfyUI API server
└── comfyui_character_generator.py  # Character image generation
```

## Directory Purposes

**config/**
- Purpose: Application configuration management
- Contains: ConfigManager class for API keys, LLM provider settings
- Key files: `config_manager.py`
- Subdirectories: None

**models/**
- Purpose: Data models and domain objects
- Contains: ProjectData model, TTS models (optional)
- Key files: `project_data.py`
- Subdirectories: `piper/` (TTS model files)

**services/**
- Purpose: Business logic and external service integration
- Contains: LLM service, file service, content generator, ComfyUI service
- Key files: `llm_service.py` (LLM integration), `content_generator.py` (content creation), `comfyui_service.py` (image generation)
- Subdirectories: None

**gui/**
- Purpose: User interface components
- Contains: Main window, tabs, dialogs
- Key files: `main_window.py` (main application window)
- Subdirectories: `tabs/` (feature tabs), `dialogs/` (settings dialog)

**gui/tabs/**
- Purpose: Individual feature tabs
- Contains: BaseTab abstract class and concrete tab implementations
- Key files: `base_tab.py` (abstract base), `synopsis_input_tab.py`, `scripts_tab.py`, `scenes_tab.py`, etc.
- Subdirectories: None

**utils/**
- Purpose: Shared utility functions
- Contains: JSON utilities, UI helpers, file utilities, Word converter
- Key files: `json_utils.py`, `ui_helpers.py`, `word_converter.py`
- Subdirectories: None

**prompts/**
- Purpose: Project data storage (file-based database)
- Contains: Project folders with characters, scenes, scripts, mappings
- Structure: `{project_name}/characters/*.json`, `{project_name}/scenes/**/*.json`, `{project_name}/*_episodes/**/*.md`
- Subdirectories: One per project

**output/**
- Purpose: Generated files (TTS audio, images)
- Contains: TTS audio files
- Subdirectories: `tts/`

## Key File Locations

**Entry Points:**
- `main.py` - Application entry point, service initialization
- `comfyui_api_server.py` - Flask API server for ComfyUI integration

**Configuration:**
- `config/config_manager.py` - Settings management
- `requirements.txt` - Python dependencies

**Core Logic:**
- `services/llm_service.py` - LLM API integration (Gemini, OpenAI, Anthropic)
- `services/content_generator.py` - Content generation orchestration
- `services/file_service.py` - File I/O operations
- `gui/main_window.py` - Main window and tab management

**Testing:**
- `test_comfyui.py` - ComfyUI integration test
- No dedicated test directory

**Documentation:**
- `README.md` - Project overview and setup instructions
- `*_TAB_IMPLEMENTATION.md` - Tab implementation docs
- `STORAGE_FORMAT.md` - Data storage format documentation

## Naming Conventions

**Files:**
- snake_case.py for all Python modules
- {feature}_tab.py for GUI tabs
- {feature}_service.py for service classes
- PascalCase class names inside files

**Directories:**
- snake_case for all directories
- Plural for collections: tabs/, dialogs/, services/, utils/

**Special Patterns:**
- __init__.py for Python package markers
- __pycache__/ for compiled Python bytecode (gitignored)

## Where to Add New Code

**New Feature Tab:**
- Primary code: `gui/tabs/{feature}_tab.py`
- Base class: Extend `gui/tabs/base_tab.py`
- Registration: Add to `gui/main_window.py` `_initialize_tabs()`

**New Service:**
- Implementation: `services/{service_name}_service.py`
- Initialization: Add to `main.py` service initialization
- Usage: Inject into MainWindow or tabs as needed

**New Utility:**
- Implementation: `utils/{utility_name}.py`
- Import from any layer

**New Dialog:**
- Implementation: `gui/dialogs/{dialog_name}_dialog.py`
- Usage: Call from main_window.py or tabs

## Special Directories

**prompts/**
- Purpose: User project data (not committed to git, user-generated)
- Source: Created and managed by application
- Committed: Structure documented, actual data not committed

**output/**
- Purpose: Generated files (TTS audio, images)
- Source: Created by application
- Committed: No (output files not committed)

**models/piper/**
- Purpose: TTS model files
- Source: Downloaded separately
- Committed: No (large binary files)

**__pycache__/**
- Purpose: Python compiled bytecode
- Source: Auto-generated by Python interpreter
- Committed: No (.gitignored)

---

*Structure analysis: 2026-01-19*
*Update when directory structure changes*
