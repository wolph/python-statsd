API Reference
=============

.. toctree::
   :maxdepth: 2

   statsd.client
   statsd.connection
   statsd.timer
   statsd.counter
   statsd.gauge
   statsd.average
   statsd.raw

Everything is exported from the top-level ``statsd`` package, so
``statsd.Timer`` and ``statsd.timer.Timer`` are the same class. The
module pages above are the reference for each metric type, and the two
entries below are the shortcuts the package adds on top.

.. autofunction:: statsd.increment

.. autofunction:: statsd.decrement

.. data:: statsd.__version__

   The installed version, read from the package metadata.
