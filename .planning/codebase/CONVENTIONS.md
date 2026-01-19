# Coding Conventions

**Analysis Date:** 2026-01-19

## Naming Patterns

**Files:**
- snake_case for all Python files (main.py, config_manager.py, llm_service.py)
- Descriptive names with category suffix: *_service.py, *_tab.py, *_dialog.py
- Test files: test_*.py (e.g., test_comfyui.py)

**Functions:**
- snake_case for all functions
- Private methods: _leading_underscore (e.g., `_call_gemini`, `_setup_window`)
- Descriptive names: get_*, set_*, create_*, load_*, save_*
- Korean language names in prompts/comments for domain-specific terms

**Variables:**
- snake_case for variables
- Descriptive names: project_path, config_manager, file_service
- No single-letter variables except loop counters
- Korean variable names for UI labels

**Classes:**
- PascalCase for class names (ConfigManager, LLMService, BaseTab)
- Descriptive suffixes: *Service, *Tab, *Dialog, *Manager
- No prefix conventions (no I for interfaces)

**Types:**
- Python type hints used: Optional[str], Path, bool
- Not extensively used throughout codebase

## Code Style

**Formatting:**
- 4-space indentation (Python standard)
- No formatter config detected (.prettierrc, .black, etc.)
- Mixed line lengths (no strict limit enforced)

**Linting:**
- No linter config detected (.pylintrc, .flake8, etc.)

**Docstrings:**
- Triple-quoted docstrings for modules and classes
- Function docstrings present but not consistent
- Korean language used in comments and docstrings
- Args/Returns format used in some docstrings

## Import Organization

**Order:**
1. Standard library imports (os, sys, pathlib, argparse)
2. Third-party packages (tkinter, flask)
3. Local application imports (config, models, services, gui, utils)

**Grouping:**
- Blank lines between import groups
- Relative imports from local packages: `from config.config_manager import ConfigManager`
- Absolute imports for standard library

**Path Handling:**
- pathlib.Path preferred over os.path
- Path objects used consistently

## Error Handling

**Patterns:**
- Try/except blocks at service boundaries
- User-friendly error messages in Korean
- messagebox for GUI error display
- ImportError for missing optional dependencies with install instructions

**Error Types:**
- ValueError for invalid configuration
- ImportError for missing packages
- General Exception catching in GUI event handlers

**Lazy Imports:**
- Optional dependencies imported lazily in `services/llm_service.py`
- Global module references with lazy initialization pattern

## Logging

**Framework:**
- print() statements for console output
- No structured logging framework

**Patterns:**
- Korean language messages: `print(f"[시작] prompts 폴더: {prompts_path}")`
- Status messages for major operations
- No log levels (debug, info, warn, error)

## Comments

**When to Comment:**
- Module-level docstrings explain purpose
- Korean language comments for business logic
- English comments for technical details
- Comments explain "why" for non-obvious code

**Docstrings:**
- Module docstrings at top of file
- Class docstrings describe purpose
- Method docstrings use Args/Returns format (not consistent)
- Korean language used for domain-specific descriptions

**TODO Comments:**
- Not observed in codebase
- Implementation status tracked in README.md

## Function Design

**Size:**
- Functions range from 10-100+ lines
- Large functions present (not strictly limited)
- Helper methods extracted with _ prefix

**Parameters:**
- Multiple parameters common (5-8 parameters)
- Dependency injection used (config_manager, file_service passed in)
- Type hints used inconsistently

**Return Values:**
- Optional[str] for functions that may fail
- bool for save/validation methods
- Explicit return statements

## Module Design

**Exports:**
- Classes imported directly: `from gui.main_window import MainWindow`
- No __all__ declarations
- Public API not formally defined

**Package Structure:**
- __init__.py files present but empty
- No barrel file pattern

---

*Convention analysis: 2026-01-19*
*Update when patterns change*
