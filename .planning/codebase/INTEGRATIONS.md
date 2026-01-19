# External Integrations

**Analysis Date:** 2026-01-19

## APIs & External Services

**AI/LLM Services:**
- Google Gemini - Script content generation, character descriptions, scene analysis
  - SDK/Client: google-generativeai package
  - Auth: API key in config (GOOGLE_API_KEY env var)
  - Models used: gemini-1.5-flash, gemini-2.0-flash-exp
  - Integration: `services/llm_service.py`

- OpenAI - Alternative LLM provider (optional)
  - SDK/Client: openai package
  - Auth: API key in config
  - Models used: Configurable via settings
  - Integration: `services/llm_service.py`

- Anthropic Claude - Alternative LLM provider (optional)
  - SDK/Client: anthropic package
  - Auth: API key in config
  - Models used: Configurable via settings
  - Integration: `services/llm_service.py`

**Image Generation:**
- ComfyUI - Character image generation via API
  - Integration method: REST API via Flask server (`comfyui_api_server.py`)
  - Endpoints: Character generation workflow
  - Integration: `services/comfyui_service.py`, `gui/tabs/comfyui_tab.py`
  - Workflows: JSON workflow files in `prompts/workflows/`

## Data Storage

**Databases:**
- None - File-based storage only

**File Storage:**
- Local filesystem - All project data stored in `prompts/` folder structure
  - Characters: `prompts/{project}/characters/*.json`
  - Scenes: `prompts/{project}/scenes/**/*.json`
  - Scripts: `prompts/{project}/*_episodes/**/*.md`
  - Mappings: `prompts/{project}/mappings/*.json`

**Caching:**
- None

## Authentication & Identity

**Auth Provider:**
- None - Local application, no user authentication

**API Keys:**
- LLM providers: Stored in config via `config/config_manager.py`
- No OAuth integrations

## Monitoring & Observability

**Error Tracking:**
- None - Console output only

**Analytics:**
- None

**Logs:**
- Standard output (stdout/stderr)
- TensorFlow warnings suppressed via environment variables

## CI/CD & Deployment

**Hosting:**
- Local desktop application
- No deployment pipeline

**CI Pipeline:**
- Not detected

## Environment Configuration

**Development:**
- Required config: LLM provider API keys
- Configuration location: Managed by `config/config_manager.py`
- Project paths: Specified via command-line arguments

**Production:**
- Same as development (local desktop app)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

---

*Integration audit: 2026-01-19*
*Update when adding/removing external services*
