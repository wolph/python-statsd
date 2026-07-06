"""statsd is a client for Etsy's statsd server, a front end/proxy for
the Graphite stats collection and graphing server."""

import importlib.metadata

from statsd.average import Average
from statsd.client import Client
from statsd.connection import Connection
from statsd.counter import Counter, decrement, increment
from statsd.gauge import Gauge
from statsd.raw import Raw
from statsd.timer import Timer

__version__: str = importlib.metadata.version('python-statsd')

__all__ = [
    'Average',
    'Client',
    'Connection',
    'Counter',
    'Gauge',
    'Raw',
    'Timer',
    'decrement',
    'increment',
]
