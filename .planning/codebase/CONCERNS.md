# Codebase Concerns

**Analysis Date:** 2026-01-19

## Tech Debt

**No automated testing:**
- Issue: Application has no automated test suite (only manual testing)
- Files: Entire codebase lacks tests
- Why: Rapid prototyping phase, GUI-heavy application
- Impact: Refactoring risk, no regression detection, manual QA required
- Fix approach: Add pytest framework, start with service layer tests (`services/llm_service.py`, `services/content_generator.py`)

**Lazy import pattern inconsistency:**
- Issue: Only LLM packages use lazy import, other optional dependencies don't
- File: `services/llm_service.py` (has lazy imports), `main.py` (tkinterdnd2 has fallback but not lazy)
- Why: LLM packages added later with optimization consideration
- Impact: Inconsistent startup performance, some optional deps cause import errors
- Fix approach: Standardize optional dependency handling across codebase

**No error logging framework:**
- Issue: Only print() statements for logging, no structured logging
- Files: All service files use print() for status messages
- Why: Simple console output sufficient during development
- Impact: No log persistence, hard to debug production issues, no log levels
- Fix approach: Add Python logging module with file handler and levels

## Known Bugs

**No known bugs documented:**
- No TODO, FIXME, or bug comments detected
- README shows features as "구현 완료" (implementation complete)

## Security Considerations

**API keys in config:**
- Risk: API keys stored in config file without encryption
- Files: `config/config_manager.py` manages keys
- Current mitigation: Config file should be gitignored (verify .gitignore)
- Recommendations: Use environment variables or secure keychain storage, encrypt config file

**No input validation on LLM prompts:**
- Risk: User input passed directly to LLM without sanitization
- Files: `services/content_generator.py`, tab files that call LLM
- Current mitigation: None detected
- Recommendations: Add input length limits, sanitize special characters, rate limiting

## Performance Bottlenecks

**Synchronous LLM calls block GUI:**
- Problem: LLM API calls made synchronously, freezing GUI during generation
- Files: `services/llm_service.py` calls, `gui/tabs/*.py` generation buttons
- Measurement: 5-30 second freeze during content generation
- Cause: No threading for API calls
- Improvement path: Use threading.Thread or asyncio for LLM calls, add progress indicators

**No caching for repeated LLM calls:**
- Problem: Same prompts generate new API calls every time
- Files: `services/content_generator.py`
- Measurement: Multiple API calls for similar content
- Cause: No caching layer
- Improvement path: Add simple file-based or memory cache for prompt/response pairs

## Fragile Areas

**File path handling:**
- Why fragile: Multiple ways to find prompts folder (`main.py`, `gui/main_window.py`)
- Files: `main.py` `find_prompts_folder()`, `gui/main_window.py` `_find_prompts_folder()`
- Common failures: Incorrect project path when running from different directories
- Safe modification: Consolidate path finding logic to one location
- Test coverage: None

**Tab initialization order:**
- Why fragile: Tabs depend on services initialized in specific order
- Files: `main.py` service initialization, `gui/main_window.py` `_initialize_tabs()`
- Common failures: NoneType errors if service initialization fails
- Safe modification: Add validation that all services initialized before creating tabs
- Test coverage: None

## Scaling Limits

**Local file storage:**
- Current capacity: Limited by disk space, no practical limit
- Limit: Large projects with many scenes/episodes may have slow file I/O
- Symptoms at limit: Slow project loading, lag when switching projects
- Scaling path: Add project indexing, lazy load project data, consider SQLite for structured data

**LLM API rate limits:**
- Current capacity: Depends on API tier (Gemini free tier: 15 RPM)
- Limit: Batch operations hit rate limits
- Symptoms at limit: API errors during bulk generation
- Scaling path: Add rate limiting with queue, retry logic with backoff

## Dependencies at Risk

**tkinterdnd2:**
- Risk: Optional dependency, may not work on all platforms
- Impact: Drag-and-drop feature disabled if not installed
- Files: `main.py` tries import with fallback
- Migration plan: Already has fallback to standard tk.Tk()

## Missing Critical Features

**Undo/Redo functionality:**
- Problem: No undo for edits or content generation
- Current workaround: Manual file backups, OS-level file recovery
- Blocks: User confidence in editing, accidental data loss risk
- Implementation complexity: Medium (need history tracking per tab)

**Auto-save:**
- Problem: No auto-save, changes lost if application crashes
- Current workaround: Manual save, README mentions "자동 저장" but unclear if implemented
- Blocks: Data loss on crashes
- Implementation complexity: Low (periodic save timer + dirty flag tracking)

**Search/Filter functionality:**
- Problem: No search across projects, characters, scenes
- Current workaround: Manual browsing through UI
- Blocks: Hard to find specific content in large projects
- Implementation complexity: Medium (need indexing + search UI)

## Test Coverage Gaps

**Service layer completely untested:**
- What's not tested: LLM integration, content generation, file operations
- Files: `services/llm_service.py`, `services/content_generator.py`, `services/file_service.py`
- Risk: Breaking changes undetected, API integration failures
- Priority: High
- Difficulty to test: Medium (need to mock external APIs)

**GUI layer untested:**
- What's not tested: All tab functionality, dialogs, main window
- Files: `gui/**/*.py`
- Risk: UI regressions, broken button handlers
- Priority: Medium
- Difficulty to test: High (requires GUI testing framework like pytest-qt)

---

*Concerns audit: 2026-01-19*
*Update as issues are fixed or new ones discovered*
