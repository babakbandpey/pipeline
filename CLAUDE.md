# CLAUDE.md — pipeline

## Project Overview

RAG (Retrieval-Augmented Generation) chatbot framework with support for Web, PDF, JSON, and YouTube data sources. Built in Python with LangChain, ChromaDB, and Docker support. Provides a modular pipeline for ingesting, embedding, and querying documents via multiple LLM providers.

- **Language / Runtime**: Python 3.11+
- **Framework**: LangChain, ChromaDB, FastAPI/Django
- **Architecture**: Layered pipeline — ingestion, embedding, retrieval, generation
- **Package / Namespace**: `pipeline`

---

## Required Skills — ALWAYS Invoke These

These skills **must** be invoked when the relevant situation arises. Never skip them.

| Situation | Skill |
|-----------|-------|
| Before any new feature or screen | `superpowers:brainstorming` |
| Planning multi-step changes | `superpowers:writing-plans` |
| Writing or fixing core logic | `superpowers:test-driven-development` |
| First sign of a bug or failure | `superpowers:systematic-debugging` |
| Before completing a feature branch | `superpowers:requesting-code-review` |
| Before claiming any task done | `superpowers:verification-before-completion` |
| Working on UI / frontend | `frontend-design:frontend-design` |
| After implementing — reviewing quality | `simplify` |

---

## Architecture

```
pipeline/
├── pipeline/        ← Core pipeline modules (ingestion, retrieval, generation)
├── tests/           ← pytest test suite
├── scripts/         ← Utility scripts (check_encoding.py, etc.)
├── docs/            ← Documentation
├── examples/        ← Usage examples
├── requirements.txt ← Production dependencies
├── pyproject.toml   ← Project metadata and build config
├── setup.py         ← Package setup
├── Dockerfile       ← Container image
└── docker-compose.yaml ← Local development compose
```

### Layer Rules
- `pipeline/` core modules must not import from `tests/` or `scripts/`
- All external API calls must be wrapped in dedicated provider modules
- Configuration via environment variables — no hardcoded credentials

---

## Coding Conventions

- [ ] All models are **immutable** — use dataclasses or Pydantic models
- [ ] Functions are **pure** where possible — no hidden side effects
- [ ] No hardcoded strings — use config/environment variables
- [ ] Strict typing everywhere — type hints on all functions
- [ ] **Max 200 lines per file** — extract a class or module when approaching the limit

---

## Engineering Principles

### File Size
- **200-line maximum per file** — extract a class, function, or module when approaching the limit

### DRY · SOLID · KISS · YAGNI
- Extract shared logic into named utilities; never copy-paste
- Single Responsibility: one class/function does one thing
- Don't add features not yet needed
- Delete dead code immediately

### TDD
- Write the failing test first, make it pass, then refactor
- Test names describe behaviour: `"should chunk pdf into paragraphs"`
- One assertion per test — keep tests focused and readable

### Commit hygiene
- Follow Conventional Commits: `feat: ...` / `fix: ...` / `chore: ...`
- The `commit-msg` hook enforces this automatically

---

## Build Commands

```bash
pip install -r requirements.txt    # Install dependencies
pytest                             # Run tests
ruff check .                       # Lint
ruff check . && pytest             # Full smoke check — used in CI and pre-commit
```

---

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | This file — project conventions and session startup |
| `version.txt` | Semantic version (MAJOR.MINOR.PATCH) |
| `requirements.txt` | Production dependencies |
| `pyproject.toml` | Project metadata and build config |
| `.github/workflows/ci.yml` | CI on PRs and non-main branches |
| `.github/workflows/release.yml` | Release automation with semver |
| `.githooks/pre-commit` | Lint and test on staged changes |
| `.githooks/commit-msg` | Conventional Commits enforcement |
| `scripts/install-hooks.sh` | One-time hook installer |

---

## Starting a New Session

1. Read this file
2. Run `ruff check . && pytest` to confirm everything passes
3. Invoke `superpowers:brainstorming` before touching any feature
4. Follow the Required Skills table — every skill is mandatory, not optional
