Introduction
============

`statsd` is a client for Etsy's statsd server, a front end/proxy for the
Graphite stats collection and graphing server.

* Graphite
    - http://graphite.wikidot.com
* Statsd 
    - code: https://github.com/etsy/statsd
    - blog post: http://codeascraft.etsy.com/2011/02/15/measure-anything-measure-everything/


Install
=======

To install simply execute `python setup.py install`.
If you want to run the tests first, run `python setup.py nosetests`


Usage
=====

To get started real quick, just try something like this:

Basic Usage
-----------

Timers
^^^^^^

    >>> import statsd
    >>> 
    >>> timer = statsd.Timer('MyApplication')
    >>> 
    >>> timer.start()
    >>> # do something here
    >>> timer.stop('SomeTimer')


Counters
^^^^^^^^

    >>> import statsd
    >>> 
    >>> counter = statsd.Counter('MyApplication')
    >>> # do something here
    >>> counter += 1


Gauge
^^^^^

    >>> import statsd
    >>>
    >>> gauge = statsd.Counter('MyApplication')
    >>> # do something here
    >>> gauge.send('SomeName', value)
    

Advanced Usage
--------------

    >>> import statsd
    >>> 
    >>> # Open a connection to `server` on port `1234` with a `50%` sample rate
    >>> statsd_connection = statsd.Connection(
    ...     host='server',
    ...     port=1234,
    ...     sample_rate=0.5,
    ... )
    >>> 
    >>> # Create a client for this application
    >>> statsd_client = statsd.Client(__name__, statsd_connection)
    >>>
    >>> class SomeClass(object):
    ...     def __init__(self):
    ...         # Create a client specific for this class
    ...         self.statsd_client = statsd_client.get_client(
    ...             self.__class__.__name__)
    ...
    ...     def do_something(self):
    ...         # Create a `timer` client
    ...         timer = self.statsd_client.get_client(class_=statsd.Timer)
    ...
    ...         # start the measurement
    ...         timer.start()
    ...
    ...         # do something
    ...         timer.interval('intermediate_value')
    ...
    ...         # do something else
    ...         timer.stop('total')

