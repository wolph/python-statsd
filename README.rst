Introduction
============

.. image:: https://travis-ci.org/WoLpH/python-statsd.svg?branch=master
    :alt: Test Status
    :target: https://travis-ci.org/WoLpH/python-statsd

.. image:: https://coveralls.io/repos/WoLpH/python-statsd/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://coveralls.io/r/WoLpH/python-statsd?branch=master

.. image:: https://landscape.io/github/WoLpH/python-statsd/master/landscape.png
   :target: https://landscape.io/github/WoLpH/python-statsd/master
   :alt: Code Health

`statsd` is a client for Etsy's statsd server, a front end/proxy for the
Graphite stats collection and graphing server.

Links
-----

 - The source: https://github.com/WoLpH/python-statsd
 - Project page: https://pypi.python.org/pypi/python-statsd
 - Reporting bugs: https://github.com/WoLpH/python-statsd/issues
 - Documentation: http://python-statsd.readthedocs.io/en/latest/
 - My blog: http://w.wol.ph/
 - Statsd: https://github.com/etsy/statsd
 - Graphite: http://graphite.wikidot.com

Install
-------

To install simply execute `python setup.py install`.
If you want to run the tests first, run `python setup.py nosetests`


Usage
-----

To get started real quick, just try something like this:

Basic Usage
~~~~~~~~~~~

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
    >>> gauge = statsd.Gauge('MyApplication')
    >>> # do something here
    >>> gauge.send('SomeName', value)


Raw
^^^

Raw strings should be e.g. pre-summarized data or other data that will
get passed directly to carbon.  This can be used as a time and
bandwidth-saving mechanism sending a lot of samples could use a lot of
bandwidth (more b/w is used in udp headers than data for a gauge, for
instance).



    >>> import statsd
    >>>
    >>> raw = statsd.Raw('MyApplication', connection)
    >>> # do something here
    >>> raw.send('SomeName', value, timestamp)

The raw type wants to have a timestamp in seconds since the epoch (the
standard unix timestamp, e.g. the output of "date +%s"), but if you leave it out or
provide None it will provide the current time as part of the message

Average
^^^^^^^

    >>> import statsd
    >>>
    >>> average = statsd.Average('MyApplication', connection)
    >>> # do something here
    >>> average.send('SomeName', 'somekey:%d'.format(value))


Connection settings
^^^^^^^^^^^^^^^^^^^

If you need some settings other than the defaults for your ``Connection``,
you can use ``Connection.set_defaults()``.
    
    >>> import statsd
    >>> statsd.Connection.set_defaults(host='localhost', port=8125, sample_rate=1, disabled=False)

Every interaction with statsd after these are set will use whatever you
specify, unless you explicitly create a different ``Connection`` to use
(described below).

Defaults:

- ``host`` = ``'localhost'``
- ``port`` = ``8125``
- ``sample_rate`` = ``1``
- ``disabled`` = ``False``


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
    ...         timer.intermediate('intermediate_value')
    ...
    ...         # do something else
    ...         timer.stop('total')

If there is a need to turn *OFF* the service and avoid sending UDP messages,
the ``Connection`` class can be disabled by enabling the disabled argument::

    >>> statsd_connection = statsd.Connection(
    ...     host='server',
    ...     port=1234,
    ...     sample_rate=0.5,
    ...     disabled=True
    ... )

If logging's level is set to debug the ``Connection`` object will inform it is
not sending UDP messages anymore.
