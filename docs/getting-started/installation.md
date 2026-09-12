# Installation

```bash
pip install python-statsd
```

or, with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install python-statsd
```

The package has no runtime dependencies and supports CPython 3.10 and
newer, plus PyPy.

## Note on the package name

This project is published on PyPI as `python-statsd` and installs a module
called `statsd`. A different project, jsocol's client, is published as
`statsd` and installs a module called `statsd` as well. Installing both in
one environment leaves you with whichever module was written last, so pick
one and stay with it.

## What you need on the other end

A statsd server listening on UDP. The defaults point at `localhost:8125`,
which is where [Etsy's statsd](https://github.com/etsy/statsd) listens
unless told otherwise. Nothing in this library reads from the socket, so a
server that is down produces no error, only missing graphs.

## Checking the installation

```python
import statsd

print(statsd.__version__)
```

If that prints a version, the client is installed. It does not tell you
whether a server is listening, and the next page explains why that is by
design.
