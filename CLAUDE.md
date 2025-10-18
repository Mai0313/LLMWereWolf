# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project template designed to bootstrap production-ready projects quickly. The codebase follows a modern `src/` layout with comprehensive tooling for development, testing, documentation, and deployment.

**Package name**: `repo_template`
**Python support**: 3.10, 3.11, 3.12, 3.13
**Dependency manager**: `uv`
**Documentation**: MkDocs Material with mkdocstrings

## Common Development Commands

### Environment Setup

```bash
make uv-install           # Install uv (one-time setup)
uv sync                   # Install base dependencies
uv sync --group test      # Include test dependencies
uv sync --group docs      # Include docs dependencies
uv sync --group dev       # Include dev tools (pre-commit, poe, notebook)
```

### Running Tests

```bash
make test                 # Run pytest with coverage
pytest                    # Direct pytest invocation
pytest -vv                # Verbose output
pytest tests/test_*.py    # Run specific test file
uv run pytest -n auto     # Run with parallel execution (xdist)
```

### Code Quality

```bash
make format               # Run all pre-commit hooks (ruff, mypy, etc.)
pre-commit run -a         # Same as make format
```

### Documentation

```bash
make gen-docs             # Generate API docs from src/ and scripts/
uv run mkdocs serve       # Serve docs at http://localhost:9987
uv run poe docs           # Generate and serve (requires dev group)
```

### CLI Entry Points

The project defines two CLI entry points (both execute the same function):

```bash
uv run repo_template      # Primary CLI entrypoint
uv run cli                # Alternative entrypoint
```

### Building and Publishing

```bash
uv build                  # Build wheel and sdist to dist/
UV_PUBLISH_TOKEN=... uv publish   # Publish to PyPI
```

### Running from PyPI

After publishing, the CLI can be run without installation:

```bash
uvx repo_template                              # Run latest from PyPI
uvx --from repo_template==0.1.0 repo_template  # Run specific version
```

### Maintenance

```bash
make clean                # Remove caches, artifacts, generated docs
```

## Project Architecture

### Source Layout

- **`src/repo_template/`**: Main package code
  - `cli.py`: CLI entry point with example `Response` Pydantic model and `main()` function
  - Uses Pydantic models with `Field()` descriptors and Google-style docstrings

### Testing Infrastructure

- **Test directory**: `tests/`
- **Test discovery**: Files matching `test_*.py`
- **Coverage**: Minimum 80% required (`--cov-fail-under=80`)
- **Parallel execution**: Enabled via pytest-xdist (`-n=auto`)
- **Reports**: Generated in `.github/reports/` (coverage.xml, pytest_logs.log)
- **Async support**: `asyncio_mode = "auto"` for async test functions

### Documentation Generation

- **Script**: `scripts/gen_docs.py` (async, supports concurrency)
- **Modes**:
  - `--mode class`: Generate docs per class (default)
  - `--mode file`: Generate docs per file
- **File types**: Supports `.py` and `.ipynb` (notebooks)
- **Execution**: `--execute` flag to run notebooks before conversion
- **Output**: Preserves source folder structure in docs
- **Usage**:
  ```bash
  python scripts/gen_docs.py --source ./src --output ./docs/Reference gen_docs
  ```

### Docker and Services

- **Dockerfile**: Multi-stage build with uv/uvx and Node.js
- **docker-compose.yaml**: Includes optional services:
  - `redis` (port 6379)
  - `postgresql` (port 5432)
  - `mongodb` (port 27017)
  - `mysql` (port 3306)
  - `app`: Example service running the CLI
- **Configuration**: Via `.env` file (see README.md for keys)

### CI/CD Workflows

All workflows are in `.github/workflows/`:

- **test.yml**: Runs pytest on Python 3.10-3.13 for PRs to main/release/\* (ignores markdown files)
- **code-quality-check.yml**: Runs pre-commit hooks on PRs
- **deploy.yml**: Builds and deploys MkDocs to GitHub Pages on push to main and tags `v*`
- **build_package.yml**: Builds wheel/sdist on tags `v*`, generates changelog via git-cliff
- **build_image.yml**: Builds and pushes Docker image to GHCR on main and tags `v*`
- **release_drafter.yml**: Maintains draft releases from Conventional Commits
- **auto_labeler.yml**: Auto-applies PR labels based on `.github/labeler.yml`
- **code_scan.yml**: Runs gitleaks for secret detection
- **semantic-pull-request.yml**: Enforces Conventional Commit PR titles

### Code Style and Linting

- **Linter**: ruff with extensive rule sets (see pyproject.toml)
- **Line length**: 99 characters (Google Python Style Guide)
- **Naming**: snake_case (functions/vars), PascalCase (classes), UPPER_CASE (constants)
- **Type hints**: Required on public functions; mypy with Pydantic plugin enabled
- **Docstrings**: Google-style (configured in mkdocstrings)
- **Allowed confusables**: Chinese punctuation marks are allowed
- **Per-file ignores**:
  - `tests/*`: Ignore S101 (assert), ANN (annotations), SLF001 (private access)
  - `*.ipynb`: Ignore T201 (print), F401 (unused imports), S105, F811, ANN, PERF, SLF

### Dependency Management

```bash
uv add <package>              # Add production dependency
uv add <package> --dev        # Add development dependency
uv remove <package>           # Remove dependency
```

### Conventions

- **Commit style**: Conventional Commits enforced for PR titles
- **Versioning**: PEP 440 via `dunamai` in CI from git tags
- **Changelog**: Generated via `git-cliff` from conventional commits
- **Pre-commit stages**: Runs on pre-commit, post-checkout, post-merge, post-rewrite

## Testing Notes

- Tests run in parallel by default (`-n=auto`)
- Coverage reports committed to `.github/reports/`
- PR comments show coverage summary automatically
- Use markers for special cases:
  - `@pytest.mark.slow`: For slow tests
  - `@pytest.mark.skip_when_ci`: Skip in CI/CD
- Async tests are automatically detected and run

## Publishing Workflow

1. Tag with version: `git tag v0.1.0`
2. Push tag: `git push origin v0.1.0`
3. CI builds package and Docker image
4. Optional: Auto-publish to PyPI (requires UV_PUBLISH_TOKEN secret)
5. Changelog auto-generated via git-cliff
6. Draft release created via release_drafter

## Documentation System

- **Serve locally**: `uv run mkdocs serve` (http://localhost:9987)
- **Deploy**: `mkdocs gh-deploy` or push to main (auto-deploys)
- **API docs**: Auto-generated from docstrings via mkdocstrings
- **Features**: Inheritance diagrams, markdown-exec, MathJax support
- **Bilingual**: Scaffolded for multiple languages (en, zh-TW, zh-CN)

## Package Configuration

- **Build backend**: hatchling
- **Entry points**: Defined in `[project.scripts]` in pyproject.toml
- **Include in wheel**: `src/repo_template`
- **Sdist excludes**: Hidden files/dirs (.github, .devcontainers, .venv, etc.)

## Important Paths

- Source code: `src/repo_template/`
- Tests: `tests/`
- Documentation: `docs/`
- Scripts: `scripts/`
- CI reports: `.github/reports/`
- Cache directories: `.cache/` (pytest, ruff, mypy, logfire)
