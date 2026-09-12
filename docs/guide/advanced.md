# Advanced usage

The pattern this library is built around: one connection for the
application, one client per component, and metric names that assemble
themselves from the client tree instead of from string formatting at
every call site.

## A client per class

```python
import statsd

connection = statsd.Connection(host='server', port=1234, sample_rate=0.5)
app_client = statsd.Client(__name__, connection)


class SomeClass:
    def __init__(self):
        self.statsd_client = app_client.get_client(type(self).__name__)

    def do_something(self):
        timer = self.statsd_client.get_client(class_=statsd.Timer)
        timer.start()
        # do something
        timer.intermediate('intermediate_value')
        # do something else
        timer.stop('total')


SomeClass().do_something()
```

Each class gets its own namespace under the module name, and the timer
inherits it. Nothing in `do_something` mentions where the metric ends up,
which is the point: renaming the class renames its metrics.

## Switching type without renaming

`get_client()` takes a class, so one named client can spawn every metric
type under the same name:

```python
import statsd

component = statsd.Client('MyApplication.worker')

timer = component.get_client(class_=statsd.Timer)
counter = component.get_client('jobs', class_=statsd.Counter)
gauge = component.get_client('queue', class_=statsd.Gauge)
```

The shortcut methods say the same thing with less ceremony:

```python
import statsd

component = statsd.Client('MyApplication.worker')

timer = component.get_timer()
counter = component.get_counter('jobs')
gauge = component.get_gauge('queue')
average = component.get_average('batch_size')
raw = component.get_raw('summary')
```

Called on a client that is already a metric type, `get_client()` without
a class keeps that type:

```python
import statsd

counters = statsd.Counter('MyApplication')
cache = counters.get_client('cache')  # also a Counter

cache.increment('hit')
```

## Timing a method with the decorator

```python
import statsd

timer = statsd.Client('MyApplication').get_timer()


class Worker:
    @timer.decorate
    def process(self):
        pass


Worker().process()
```

The metric is `MyApplication.process`. Note what it is not: the decorator
sees the function, not the class, so two classes with a `process` method
sharing one timer report into the same name. Give the second one its own
client, or pass an explicit name to `decorate`.

## Sub-clients share the connection

```python
import statsd

connection = statsd.Connection(host='server', port=1234)
root = statsd.Client('MyApplication', connection)

child = root.get_client('database')
assert child.connection is connection
```

One socket serves the whole tree. That matters on a process creating
clients per request: the clients are cheap, and the connection they copy
is the expensive part you are not re-creating.
