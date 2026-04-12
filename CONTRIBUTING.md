# Contributing to pipeline

## Local Setup

1. Install Python 3.11+ from [python.org](https://python.org)
2. Clone the repository: `git clone https://github.com/babakbandpey/pipeline.git`
3. Install dependencies: `pip install -r requirements.txt`

## Install Git Hooks

```
./scripts/install-hooks.sh
```

## Local Git Setup

Run these once after cloning:

```bash
git config pull.rebase true
git config core.autocrlf input
git config push.autoSetupRemote true
git config init.defaultBranch main
```

## Build and Test Commands

```bash
pip install -r requirements.txt    # Install dependencies
pytest                             # Run tests
ruff check .                       # Lint
ruff check . && pytest             # Full smoke check
```

## Coding Style

- Max 200 lines per file
- Type hints on all functions
- No hardcoded credentials — use environment variables
- Follow PEP 8 conventions

## Branch Naming

| Prefix | Use for |
|--------|---------|
| `feature/` | New features (`feat:` commits) |
| `fix/` | Bug fixes (`fix:` commits) |
| `chore/` | Maintenance (`chore:` commits) |
| `docs/` | Documentation (`docs:` commits) |
| `refactor/` | Code cleanup (`refactor:` commits) |
| `ci/` | CI changes (`ci:` commits) |

## PR Checklist

- [ ] Smoke check passes: `ruff check . && pytest`
- [ ] Manual test completed for changed functionality
- [ ] Updated docs if behavior changed
- [ ] Commit messages follow Conventional Commits format
