# Changelog

## 3.0.1 (2026-10-28)

### Packaging

- The build backend requirement is now `uv_build>=0.11.0,<1`, so
  distributions and build frontends that ship a newer uv can build the
  sdist without waiting for a release. Every uv minor so far shipped
  without a breaking change to the `uv_build` configuration, and CI
  builds with the current uv on every run. Prompted by @jeremycline in
  wolph/portalocker#155.
- The development extras (`dev`, `tests`, `docs` and `tox`) now require
  the versions the project is tested with (#48, #51, #55). The package
  itself still has no runtime dependencies.

### Documentation

- A two-track quickstart takes you from `pip install` to a metric on a
  graph, with or without a local Python.
- The local stack runs the official statsd daemon from
  `examples/statsd/config.js`, and `examples/grafana/import/` ships a
  dashboard that imports into an existing Grafana and asks for the
  datasource instead of assuming one.
- Every module member carries a docstring, checked with pydocstyle, and
  the documentation links point at the stable version.
- The README reports CI, CodeQL and Coveralls coverage for the master
  branch through live badges, and lists the sponsorship options.

## 3.0.0 (2026-09-12)

First release since 2.1.0 (2017). Full modernization of the project.

### Breaking changes

- Python >= 3.10 required. Python 2 support removed.
- Validation errors now raise real exceptions instead of
  `AssertionError`. `Timer` state misuse raises `RuntimeError`, and
  non-numeric `Gauge` values raise `TypeError`.
- `Connection.send` only swallows `OSError` (returning `False`), so
  other exceptions now propagate.
- The nose-specific `setup_package`/`teardown_package` hooks were
  removed from the `statsd` package.
- `statsd.__about__` was removed. Use `statsd.__version__` and the
  package metadata instead.
- The statsd.compat module (Python 2 helpers) was removed.

### Bugfixes

- The `Timer.time()` context manager now sends the metric even when
  the timed block raises an exception, matching the behavior of
  `with Timer(...)` and `@timer.decorate`.
- Timer measurements use the monotonic `time.perf_counter()` instead
  of the wall clock, so clock adjustments can't produce negative or
  wildly wrong timings.
- Passing `bytes` metric names no longer crashes on Python 3.
- `Raw.send` default timestamps no longer rely on the non-portable
  `strftime('%s')`.
- `Connection.__del__` no longer raises when construction failed
  before the socket existed.
- `Timer.time()` now yields the inner timer instance (was `None`).

### Modernization

- Packaging: `pyproject.toml` with the `uv_build` backend
  (`setup.py`/`setup.cfg` removed).
- Fully type annotated with a `py.typed` marker, checked with strict
  mypy, basedpyright, pyrefly and ty.
- Tests: pytest with 100% line and branch coverage enforced, nose
  removed.
- Linting/formatting: ruff.
- CI: GitHub Actions (Travis removed) with releases published to PyPI
  via Trusted Publishing.
- Docs: sphinx + furo on readthedocs, with the README written in
  Markdown, a getting-started and user-guide tree, and every code
  sample in the README and the docs executed by the test suite.
- Repo: CodeQL, stale-issue and dependabot workflows, plus
  `CONTRIBUTING.md` and `SECURITY.md`.

For older releases, see the git history.
