# Gauges

A gauge reports a level rather than a change. The server keeps the last
value it received and reports that, so a gauge is the right choice for
queue depth, connection-pool size, temperature, free disk, or anything
else where the current reading is the answer.

## Sending a value

```python
import statsd

gauge = statsd.Gauge('MyApplication')
gauge.send('queue_depth', 42)
```

That sets `MyApplication.queue_depth` to 42. Sending again replaces it.
Values may be {class}`int`, {class}`float` or {class}`decimal.Decimal`:

```python
import decimal

import statsd

gauge = statsd.Gauge('MyApplication')
gauge.send('load', 0.75)
gauge.send('balance', decimal.Decimal('12.34'))
```

## Relative updates

Statsd understands a signed value as an adjustment to the stored level
instead of a replacement, and {meth}`~statsd.gauge.Gauge.increment` and
{meth}`~statsd.gauge.Gauge.decrement` send that form:

```python
import statsd

gauge = statsd.Gauge('MyApplication')
gauge.increment('connections')
gauge.decrement('connections', 3)
```

Those send `+1` and `-3` rather than an absolute reading, so the server
adjusts whatever it currently holds. The delta is sent as an integer,
which means a fractional delta is truncated on its way out. Send the
level itself with {meth}`~statsd.gauge.Gauge.send` when fractions matter.

One caveat before you rely on relative updates: they are only as good as
the value the server is holding. A gauge the server has not seen since it
restarted has nothing meaningful to adjust, and what happens then is the
server's decision rather than this client's. Absolute sends do not carry
that dependency, so prefer them when the reading is available.

## Non-numeric values raise

```python
import statsd

gauge = statsd.Gauge('MyApplication')
try:
    gauge.send('queue_depth', 'forty two')
except TypeError as exception:
    print(exception)
```

This raises rather than sending, because a gauge carrying the string
`forty two` produces a metric the server accepts and silently files as
nonsense. Before 3.0.0 the check was an {exc}`AssertionError`, which
disappeared under `python -O`.
