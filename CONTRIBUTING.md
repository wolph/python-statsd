# Contributing to python-statsd

Contributions are welcome. This guide covers the development workflow.

## Quick Start

1. Clone and install:

   ```bash
   git clone https://github.com/WoLpH/python-statsd.git
   cd python-statsd
   uv sync --all-extras
   ```

2. Install git hooks:

   ```bash
   lefthook install
   ```

3. Run tests:

   ```bash
   uv run pytest
   ```

4. Lint and format:

   ```bash
   uv run ruff check statsd tests conftest.py
   uv run ruff format statsd tests conftest.py
   ```

5. Type check:

   ```bash
   uv run ty check statsd
   ```

## Development Workflow

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (package manager)
- [lefthook](https://github.com/evilmartians/lefthook) (git hooks)

### Running the Full Test Suite

```bash
uv run pytest
```

This runs the tests, the doctests in the `statsd` modules, and the coverage
report. Coverage is a gate rather than a goal: the run fails below 100%
line and branch coverage.

To run a subset:

```bash
uv run pytest tests/test_timer.py -x
```

Tests never touch the network. `conftest.py` installs a fake UDP socket, so
a test that wants to inspect what was sent reads it from that fake rather
than from a real statsd server.

`tests/test_docs_examples.py` executes every `python` block in `README.md`
and in `docs/getting-started/` and `docs/guide/`, in file order and in a
shared namespace. A sample that stops working fails the suite, so keep the
blocks runnable: no pseudo-code, and no prompts to strip.

### Everything CI Runs, Locally

`tox.ini` is the single source of truth for the matrix, and CI drives the
same file, so one command reproduces the whole pipeline in parallel:

```bash
uv run tox -p auto
```

That covers CPython 3.10 to 3.14, PyPy, ruff, the four type checkers, and
the docs build. tox-uv provisions any interpreter you are missing.

To run a single environment:

```bash
uv run tox -e mypy
```

### Pre-commit Hooks

Lefthook runs these checks in parallel on every commit:

- `ruff check` for linting
- `ruff format` for formatting (auto-fixes staged files)
- `ty check` for type checking

If a hook fails, fix the issue and commit again.

### Code Style

- **Formatter**: ruff (79-character line length)
- **Quotes**: single quotes for strings, `"""` for docstrings, which is
  what `ruff format` produces here
- **Type hints**: required on every function, method and attribute. The
  package ships a `py.typed` marker, so the annotations are part of the
  public contract.
- **Type checkers**: mypy, basedpyright, pyrefly and ty all run in strict
  mode and all have to be clean. Reach for a redesign before a
  `# type: ignore`.

### Building Documentation

```bash
uv run tox -e docs
```

Sphinx runs with `-W`, so a warning fails the build. The rendered HTML
lands in the environment's temporary directory, and the path is printed at
the end of the run.

## Pull Request Guidelines

1. Branch off `develop` and target `develop` with the pull request.
2. Include tests for new behaviour, and keep coverage at 100%.
3. All CI checks have to pass: tests, lint, type checking and docs.
4. Support the full matrix: CPython 3.10 to 3.14 and PyPy.

## Reporting Bugs

File issues at https://github.com/WoLpH/python-statsd/issues.

Include:

- Your operating system and Python version
- Steps to reproduce
- Expected versus actual behaviour
- The statsd server you are sending to, if the problem is on the wire
