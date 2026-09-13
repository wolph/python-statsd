"""A client for statsd, the metrics aggregation daemon.

statsd started at Etsy and now lives at https://github.com/statsd/statsd.
It sits in front of Graphite, aggregating the metrics this client sends
over UDP and flushing the results onwards.
"""

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
