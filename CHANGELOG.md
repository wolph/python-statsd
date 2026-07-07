# Changelog

## 3.0.0 (unreleased)

First release since 2.1.0 (2017). Full modernization of the project.

### Breaking changes

- Python >= 3.10 required; Python 2 support removed.
- Validation errors now raise real exceptions instead of
  `AssertionError`: `Timer` state misuse raises `RuntimeError`;
  non-numeric `Gauge` values raise `TypeError`.
- `Connection.send` only swallows `OSError` (returning `False`);
  other exceptions now propagate.
- The nose-specific `setup_package`/`teardown_package` hooks were
  removed from the `statsd` package.
- `statsd.__about__` was removed; use `statsd.__version__` and the
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
- Fully type annotated with a `py.typed` marker; checked with strict
  mypy, basedpyright, pyrefly and ty.
- Tests: pytest with 100% line+branch coverage enforced; nose removed.
- Linting/formatting: ruff.
- CI: GitHub Actions (Travis removed) with releases published to PyPI
  via Trusted Publishing.
- Docs: sphinx + furo on readthedocs.

For older releases, see the git history.
