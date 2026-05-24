---
description: 'Python coding conventions and guidelines.'
applyTo: '**/*.py'
---

# Python Guidelines

## Philosophy
Simple, modular, maintainable. Strong typing, minimal abstractions, flat structure. Public APIs documented; side effects explicit.

## Stack
- **Python**: Latest stable (3.14.5)
- **uv**: Package/environment management (`uv sync`, `uv add`, `uv run`)
- **pyproject.toml**: Single source of truth (no requirements.txt)
- **ruff**: Linting + formatting (line length 100)
- **pytest**: Testing

## Code Standards

### Imports
- **All imports at the top of the file** — never inside a function, class, or method
- Order: stdlib → third-party → local (ruff enforces this)

### Types & Signatures
- Type hints everywhere: functions, methods, attributes
- Modern syntax: `list[str]`, `dict[str, int]`, `X | None`
- Keyword-only args for clarity: `def func(*, required: str, optional: int = 0)`

### Documentation
- **Numpy-style docstrings** for public APIs only
- Focus on *why* and edge cases, not obvious mechanics
- Document raised exceptions

### Functions & Classes
- **Single responsibility**: One clear job per unit
- Functions: action verbs, <40 lines typical
- Classes: nouns, prefer dataclasses for data
- Extract helpers when complexity grows—don't nest deep

### Error Handling
- Specific exceptions with clear messages
- Narrow `except` clauses (never bare `except`)
- Fail early: validate inputs upfront

### Modularity
- Keep modules focused (<300 lines)
- Flat structure: avoid deep nesting
- Pure functions where possible (separate I/O from logic)
- Minimal public surface; prefix internals with `_`

## Dependencies
- **Standard lib first**; justify external packages
- Favor modern Rust-based tools (ruff, uv, polars, pydantic-core)

## Testing
- Cover: happy path, edge cases (empty/None/boundaries), error conditions
- Use parametrization to stay DRY
- Test behavior, not implementation

## PR Checklist
- [ ] `ruff check && ruff format --check` passes
- [ ] Type checker passes (`pyright` or `mypy --strict`)
- [ ] Public APIs documented (Numpy docstrings)
- [ ] Tests pass with edge coverage
- [ ] No dead/commented code
- [ ] Dependencies in `pyproject.toml`
