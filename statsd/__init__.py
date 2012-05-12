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

__name__ = 'python-statsd'
__version__ = '1.5.2'
__author__ = 'Rick van Hattem'
__author_email__ = 'Rick.van.Hattem@Fawo.nl'
__description__ = ('''statsd is a client for Etsy's node-js statsd server. '''
    '''A proxy for the Graphite stats collection and graphing server.''')
__url__ ='https://github.com/WoLpH/python-statsd'

