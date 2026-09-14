<h1 align="center">python-statsd</h1>

<p align="center">
  <img src="https://raw.githubusercontent.com/wolph/python-statsd/develop/docs/_static/dataflow.svg"
       alt="Metrics leave your application over UDP, statsd aggregates them, Graphite stores and graphs them"
       width="880">
</p>

<p align="center">
  <a href="https://github.com/wolph/python-statsd/actions/workflows/ci.yml?query=branch%3Amaster"><img src="https://github.com/wolph/python-statsd/actions/workflows/ci.yml/badge.svg?branch=master" alt="CI on master"></a>
  <a href="https://github.com/WoLpH/python-statsd/actions/workflows/codeql.yml?query=branch%3Amaster"><img src="https://github.com/WoLpH/python-statsd/actions/workflows/codeql.yml/badge.svg?branch=master" alt="CodeQL status"></a>
  <a href="https://python-statsd.readthedocs.io/"><img src="https://img.shields.io/readthedocs/python-statsd?logo=readthedocs&logoColor=white" alt="Documentation"></a>
  <a href="https://coveralls.io/github/wolph/python-statsd?branch=master"><img src="https://coveralls.io/repos/github/wolph/python-statsd/badge.svg?branch=master" alt="Coverage on master"></a>
  <br>
  <a href="https://pypi.org/project/python-statsd/"><img src="https://img.shields.io/pypi/v/python-statsd.svg?logo=pypi&logoColor=white" alt="PyPI version"></a>
  <a href="https://pypi.org/project/python-statsd/"><img src="https://img.shields.io/pypi/pyversions/python-statsd.svg?logo=python&logoColor=white" alt="Supported Python versions"></a>
  <a href="https://pepy.tech/project/python-statsd"><img src="https://static.pepy.tech/badge/python-statsd" alt="Downloads"></a>
  <a href="https://github.com/WoLpH/python-statsd/blob/develop/LICENSE"><img src="https://img.shields.io/pypi/l/python-statsd.svg" alt="BSD-3-Clause licence"></a>
  <br>
  <a href="https://github.com/WoLpH/python-statsd/actions/workflows/ci.yml?query=branch%3Amaster"><img src="https://img.shields.io/badge/types-mypy%20%7C%20basedpyright%20%7C%20pyrefly%20%7C%20ty-8957e5" alt="Type checked by four checkers in CI"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Linted and formatted with ruff"></a>
</p>

`python-statsd` is a client for Etsy's statsd server, a front end and proxy
for the Graphite stats collection and graphing server. It supports Python
3.10 and newer, and it has no dependencies.

```bash
pip install python-statsd
```

```python
import statsd

counter = statsd.Counter('app')
counter += 1

with statsd.Timer('app').time('render'):
    pass  # the work you are measuring
```

Two metrics, two UDP packets, nothing blocking. A statsd server that is
down costs you graphs rather than requests.

## What goes on the wire

Every line under `udp :8125 <` in this recording is a packet the client
sent, caught by a real listener on the other end:

<p align="center">
  <img src="https://raw.githubusercontent.com/wolph/python-statsd/develop/docs/_static/demo.gif"
       alt="A terminal session sending a counter, a gauge, a timer and a sampled counter, with each UDP payload printed as it arrives"
       width="880">
</p>

Note the last one. At `sample_rate=0.5` four increments produced a single
packet, and it carries `|@0.5` so the server knows to multiply back up.

## The metric types

| Type | A burst of values becomes | Reach for it when |
| --- | --- | --- |
| `Counter` | their sum | you are counting events |
| `Gauge` | the last one | you are reporting a level |
| `Timer` | mean, median, percentiles | you are measuring duration |
| `Average` | their mean | the server should average samples |
| `Raw` | stored as sent | you already did the summarising |

```python
import statsd

counter = statsd.Counter('app')
counter.increment('requests')  # app.requests:1|c

gauge = statsd.Gauge('app')
gauge.send('queue_depth', 42)  # app.queue_depth:42|g

average = statsd.Average('app')
average.send('batch', 123)  # app.batch:123|a

raw = statsd.Raw('app')
raw.send('summary', 42, timestamp=1234567890)  # app.summary:42|r|1234567890
```

Timers come in three forms, and the context manager is the one to reach
for, because it reports the block that raised as well as the block that
did not:

```python
import statsd

timer = statsd.Timer('app')

with timer.time('render'):
    pass  # the work you are measuring


@timer.decorate
def render_page():  # sends app.render_page
    pass
```

Names build themselves when you nest clients, which keeps the string
formatting out of your call sites:

```python
import statsd

app = statsd.Client('app')
queries = app.get_client('database').get_client('queries', statsd.Counter)

queries.increment()  # app.database.queries:1|c
```

## See it working

The repository ships a compose file with statsd, Graphite and Grafana, so
you can watch a metric arrive instead of taking anyone's word for it:

```bash
docker compose up -d
uv run python examples/send_metrics.py --seconds 120
```

Then open <http://localhost:3000>. Grafana comes up with the datasource
configured and this dashboard loaded, no login in the way:

<p align="center">
  <img src="https://raw.githubusercontent.com/wolph/python-statsd/develop/docs/_static/grafana.png"
       alt="A Grafana dashboard showing request rate, render time percentiles, queue depth and packets received"
       width="880">
</p>

That screenshot is the stack in this repository, fed by
`examples/send_metrics.py` through this client. The
[local stack guide](https://python-statsd.readthedocs.io/en/latest/local-stack.html)
covers how statsd renames your metrics on the way through, and what to
check when nothing shows up.

## Configuration

Set the defaults once at startup and every client built afterwards follows:

```python
import statsd

statsd.Connection.set_defaults(host='localhost', port=8125, sample_rate=1)
```

Or build connections yourself when one destination is not enough:

```python
import statsd

connection = statsd.Connection(host='statsd-1', port=8125, sample_rate=0.1)
statsd.Counter('app.requests', connection).increment()
```

One trap worth knowing before it costs you an afternoon: a falsy argument
means "use the default", so `Connection(sample_rate=0)` sends everything.
Pass `disabled=True` to send nothing.

## Documentation

Full documentation is at
[python-statsd.readthedocs.io](https://python-statsd.readthedocs.io/).

- [Metrics](https://python-statsd.readthedocs.io/en/latest/metrics.html):
  the five types, how to choose, and the exact bytes each one writes
- [Connections](https://python-statsd.readthedocs.io/en/latest/connections.html):
  destinations, sampling, disabling, failure behaviour, threads and forks
- [Patterns](https://python-statsd.readthedocs.io/en/latest/patterns.html):
  naming, cardinality, client trees, WSGI and Celery integration
- [Local stack](https://python-statsd.readthedocs.io/en/latest/local-stack.html):
  docker compose, and how to debug a metric that never arrives

For Django, use [django-statsd](https://github.com/wolph/django-statsd),
the sister project built on this client. It times views and reports the
queries per request without you writing any of it.

## Note on the package name

This project is published on PyPI as `python-statsd` and installs a module
called `statsd`. A different project, jsocol's client, is published as
`statsd` and installs a module called `statsd` as well. Installing both in
one environment leaves you with whichever was written last, so pick one.

## Contributing

Bug reports and patches are welcome, and `CONTRIBUTING.md` covers the
development setup: `uv sync --all-extras`, `uv run pytest`, and
`uv run tox -p auto` to run everything CI runs. Every code sample in this
README and in the documentation is executed by the test suite, so a change
in behaviour tends to tell you which paragraph it just made wrong.

## Links

- Source: <https://github.com/WoLpH/python-statsd>
- Issues: <https://github.com/WoLpH/python-statsd/issues>
- Statsd: <https://github.com/etsy/statsd>
- Graphite: <https://graphiteapp.org/>
