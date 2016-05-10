from statsd.connection import Connection
from statsd.client import Client
from statsd.timer import Timer
from statsd.gauge import Gauge
from statsd.average import Average
from statsd.raw import Raw
from statsd.counter import Counter, increment, decrement

__all__ = [
    'Client',
    'Connection',
    'Timer',
    'Counter',
    'Gauge',
    'Average',
    'Raw',
    'increment',
    'decrement',
]

__package_name__ = 'python-statsd'
__version__ = '2.0.0'
__author__ = 'Rick van Hattem'
__author_email__ = 'Wolph@wol.ph'
__description__ = (
    '''statsd is a client for Etsy's node-js statsd server. '''
    '''A proxy for the Graphite stats collection and graphing server.''')
__url__ = 'https://github.com/WoLpH/python-statsd'


# The doctests in this package, when run, will try to send data on the wire.
# To keep this from happening, we hook into nose's machinery to mock out
# `Connection.send` at the beginning of testing this package, and reset it at
# the end.
_connection_patch = None


def setup_package():
    # Since we don't want mock to be a global requirement, we need the import
    # the setup method.
    import mock
    global _connection_patch
    _connection_patch = mock.patch('statsd.Connection.send')

    send = _connection_patch.start()
    send.return_value = True


def teardown_package():
    assert _connection_patch
    _connection_patch.stop()

