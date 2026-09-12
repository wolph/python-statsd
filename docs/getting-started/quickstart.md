# Quickstart

Every metric type in this library follows the same shape: create a client
with a name, then send values through it. The client owns the name and the
UDP connection, and sending never blocks, never retries and never raises
when the server is missing.

## Sending your first metrics

```python
import statsd

counter = statsd.Counter('MyApplication')
counter += 1

gauge = statsd.Gauge('MyApplication')
gauge.send('queue_depth', 42)

timer = statsd.Timer('MyApplication')
with timer.time('request'):
    pass  # the work you are measuring
```

Those three calls produce the metrics `MyApplication` (a counter),
`MyApplication.queue_depth` (a gauge) and `MyApplication.request` (a
timer). The name given to the client is the prefix, and the name given to
the call is appended to it.

## Picking a metric type

| Type | Question it answers | Server-side behaviour |
| --- | --- | --- |
| `Counter` | How many times did this happen? | Adds the deltas up per interval |
| `Gauge` | What is the level right now? | Keeps the last value it saw |
| `Timer` | How long did this take? | Computes mean, median and percentiles |
| `Average` | What is the mean of these samples? | Averages the values in the interval |
| `Raw` | (already summarised) | Passes the value straight to carbon |

When two of them look equally plausible, the deciding question is what you
want the server to do with a burst of values inside a single flush
interval: add them, forget all but the last, or summarise them.

## Naming

Metric names are dotted paths, and the dots are how Graphite builds its
tree. Sub-clients let you build that path in layers instead of formatting
strings at every call site:

```python
import statsd

app = statsd.Client('MyApplication')
database = app.get_client('database')
queries = database.get_client('queries', class_=statsd.Counter)

queries.increment()
```

That increments `MyApplication.database.queries`. The
[advanced usage guide](../guide/advanced.md) takes this further and gives
each class in an application its own client.

## Failure behaviour

A send that fails is logged and discarded. There is no exception, no
retry, and no buffering:

```python
import statsd

connection = statsd.Connection(host='statsd.invalid', port=8125)
counter = statsd.Counter('MyApplication', connection)
counter += 1
```

That code runs cleanly on a machine where the host does not resolve. It is
a deliberate trade: metrics are not worth taking an application down for.
When you do want silence rather than traffic, disable the connection
explicitly, which is covered in the
[connection guide](../guide/connection.md).
