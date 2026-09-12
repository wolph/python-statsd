# Python StatsD Client

[![Test Status](https://github.com/WoLpH/python-statsd/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/WoLpH/python-statsd/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/python-statsd.svg)](https://pypi.org/project/python-statsd/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/python-statsd.svg)](https://pypi.org/project/python-statsd/)

`python-statsd` is a client for Etsy's statsd server, a front end/proxy for
the Graphite stats collection and graphing server. It supports Python 3.10+
and has no dependencies.

## Note on the package name

This package installs the `statsd` Python module and is published on PyPI as
`python-statsd`. There is a different project published on PyPI as `statsd`
(jsocol's client) which *also* installs a `statsd` module. Installing both in
one environment will break either or both. Install exactly one of the two.

## Links

- The source: https://github.com/WoLpH/python-statsd
- Project page: https://pypi.org/project/python-statsd/
- Reporting bugs: https://github.com/WoLpH/python-statsd/issues
- Documentation: https://python-statsd.readthedocs.io/
- My blog: https://wol.ph/
- Statsd: https://github.com/etsy/statsd
- Graphite: https://graphiteapp.org/

## Install

```bash
pip install python-statsd
```

or with uv:

```bash
uv pip install python-statsd
```

## Usage

### Basic Usage

#### Timers

```python
import statsd

timer = statsd.Timer('MyApplication')
timer.start()
# do something here
timer.stop('SomeTimer')
```

Or as a context manager (the metric is also sent when the block raises an
exception):

```python
import statsd

with statsd.Timer('MyApplication').time('SomeTimer'):
    pass  # do something here
```

Or as a decorator:

```python
import statsd

timer = statsd.Timer('MyApplication')


@timer.decorate
def some_function():
    pass  # resulting timer name: MyApplication.some_function
```

#### Counters

```python
import statsd

counter = statsd.Counter('MyApplication')
# do something here
counter += 1
```

#### Gauge

```python
import statsd

gauge = statsd.Gauge('MyApplication')
# do something here
gauge.send('SomeName', 42)
```

#### Raw

Raw values should be e.g. pre-summarised data or other data that will get
passed directly to carbon. This can be used as a time and bandwidth-saving
mechanism: sending a lot of samples could use a lot of bandwidth (more b/w is
used in udp headers than data for a gauge, for instance).

```python
import statsd

raw = statsd.Raw('MyApplication')
# do something here
raw.send('SomeName', 42, timestamp=1234567890)
```

The raw type wants a timestamp in seconds since the epoch (the standard unix
timestamp, e.g. the output of `date +%s`). If you leave it out or pass `None`
the current time is used.

#### Average

```python
import statsd

average = statsd.Average('MyApplication')
# do something here
average.send('SomeName', 123)
```

#### Connection settings

If you need some settings other than the defaults for your `Connection`, you
can use `Connection.set_defaults()`:

```python
import statsd

statsd.Connection.set_defaults(
    host='localhost', port=8125, sample_rate=1, disabled=False
)
```

Every interaction with statsd after these are set will use whatever you
specify, unless you explicitly create a different `Connection` to use
(described below).

Defaults:

- `host` = `'localhost'`
- `port` = `8125`
- `sample_rate` = `1`
- `disabled` = `False`

## Advanced Usage

```python
import statsd

# Open a connection to `server` on port `1234` with a
# `50%` sample rate
statsd_connection = statsd.Connection(
    host='server',
    port=1234,
    sample_rate=0.5,
)

# Create a client for this application
statsd_client = statsd.Client(__name__, statsd_connection)


class SomeClass:
    def __init__(self):
        # Create a client specific for this class
        self.statsd_client = statsd_client.get_client(type(self).__name__)

    def do_something(self):
        # Create a `timer` client
        timer = self.statsd_client.get_client(class_=statsd.Timer)

        # start the measurement
        timer.start()

        # do something
        timer.intermediate('intermediate_value')

        # do something else
        timer.stop('total')
```

If there is a need to turn *OFF* the service and avoid sending UDP messages,
the `Connection` class can be disabled with the `disabled` argument:

```python
import statsd

statsd_connection = statsd.Connection(
    host='server',
    port=1234,
    sample_rate=0.5,
    disabled=True,
)
```

If logging's level is set to debug the `Connection` object will inform it is
not sending UDP messages anymore.
