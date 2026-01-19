# Architecture

**Analysis Date:** 2026-01-19

## Pattern Overview

**Overall:** Modular Desktop GUI Application with Service Layer

**Key Characteristics:**
- Desktop application with tkinter GUI
- Service-oriented architecture (config, models, services, GUI)
- File-based data persistence
- Event-driven GUI interactions
- Lazy loading for optional dependencies

## Layers

**GUI Layer:**
- Purpose: User interface and interaction handling
- Contains: Main window, tabs (synopsis, characters, scripts, scenes, etc.), dialogs
- Location: `gui/main_window.py`, `gui/tabs/*.py`, `gui/dialogs/*.py`
- Depends on: Services layer, models layer, utils
- Used by: User interactions

**Services Layer:**
- Purpose: Business logic and external service integration
- Contains: LLM integration, file I/O, content generation, ComfyUI integration
- Location: `services/llm_service.py`, `services/file_service.py`, `services/content_generator.py`, `services/comfyui_service.py`
- Depends on: Config layer, external APIs
- Used by: GUI layer

**Models Layer:**
- Purpose: Data structures and domain models
- Contains: ProjectData model
- Location: `models/project_data.py`
- Depends on: Nothing (pure data structures)
- Used by: Services layer, GUI layer

**Config Layer:**
- Purpose: Application configuration and settings management
- Contains: ConfigManager for API keys, provider selection
- Location: `config/config_manager.py`
- Depends on: File system
- Used by: Services layer

**Utils Layer:**
- Purpose: Shared utilities and helper functions
- Contains: JSON utilities, UI helpers, file converters
- Location: `utils/json_utils.py`, `utils/ui_helpers.py`, `utils/word_converter.py`
- Depends on: Nothing (pure functions)
- Used by: All layers

## Data Flow

**Application Startup:**

1. User runs: `python main.py [--prompts path]`
2. `main.py` initializes all services (ConfigManager, ProjectData, FileService, LLMService, ContentGenerator)
3. Creates tkinter root window
4. MainWindow initializes with services
5. MainWindow loads project list from prompts folder
6. User selects project from dropdown
7. Tabs load and display project data

**Content Generation Flow:**

1. User clicks "생성" (Generate) button in a tab
2. Tab calls `content_generator.generate_*()` method
3. ContentGenerator prepares prompt with system instructions
4. LLMService routes to appropriate provider (Gemini/OpenAI/Anthropic)
5. API call made with prompt
6. Response parsed and returned
7. Tab updates UI with generated content
8. FileService saves data to JSON/Markdown files

**State Management:**
- File-based: All state persisted to `prompts/` folder
- ProjectData model holds current project state in memory
- Each tab manages its own UI state
- No global state beyond services singleton-style instances

## Key Abstractions

**BaseTab:**
- Purpose: Abstract base class for all GUI tabs
- Location: `gui/tabs/base_tab.py`
- Pattern: Template Method pattern
- Provides: `get_tab_name()`, `create_ui()`, `update_display()`, `save()` methods

**Service Classes:**
- Purpose: Encapsulate business logic domains
- Examples: `services/llm_service.py`, `services/file_service.py`, `services/content_generator.py`
- Pattern: Service Layer pattern
- Each service manages one domain (LLM calls, files, content generation)

**ConfigManager:**
- Purpose: Centralized configuration management
- Location: `config/config_manager.py`
- Pattern: Singleton-style (one instance passed around)

## Entry Points

**CLI Entry:**
- Location: `main.py`
- Triggers: User runs `python main.py`
- Responsibilities: Initialize services, create GUI, start event loop

**GUI Event Loop:**
- Location: `gui/main_window.py` → `root.mainloop()`
- Triggers: After application initialization
- Responsibilities: Handle user interactions, button clicks, tab switches

## Error Handling

**Strategy:** Try/catch at service boundaries with user-facing error messages

**Patterns:**
- LLM calls wrapped in try/except blocks
- Errors displayed via `tkinter.messagebox`
- Lazy imports for optional dependencies (google-generativeai, openai, anthropic)
- ImportError raised with user-friendly install instructions

## Cross-Cutting Concerns

**Logging:**
- Console output via `print()` statements
- TensorFlow warnings suppressed via environment variables

**Validation:**
- API key validation in LLMService
- File path validation in FileService
- JSON schema validation (implicit)

**Error Messages:**
- User-friendly error dialogs via tkinter messagebox
- Korean language UI messages

---

*Architecture analysis: 2026-01-19*
*Update when major patterns change*
