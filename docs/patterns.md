# Patterns

Everything here is about the names. The client API is small enough to
learn in an afternoon, and the part that decides whether the graphs are
useful a year from now is how the metric names are built and who builds
them.

## Naming

A metric name is a dotted path, and Graphite turns the dots into a tree.
Build the path in layers rather than formatting strings at the call site:

```python
import statsd

app = statsd.Client('app')
database = app.get_client('database')
queries = database.get_client('queries', class_=statsd.Counter)

queries.increment()
```

That increments `app.database.queries`. Each layer owns its own segment,
so renaming a component renames its whole subtree.

`get_client()` keeps the type when you do not ask for a new one:

```python
import statsd

counters = statsd.Counter('app')
cache = counters.get_client('cache')

cache.increment('hit')
cache.increment('miss')
```

The shortcut methods say the same thing with less ceremony, one per type:

```python
import statsd

component = statsd.Client('app.worker')

timer = component.get_timer()
counter = component.get_counter('jobs')
gauge = component.get_gauge('queue')
average = component.get_average('batch_size')
raw = component.get_raw('summary')
```

## Cardinality

The rule that matters: a metric name is a series, and every distinct name
costs a file on the Graphite box forever. Names built from unbounded
values, such as user ids, request ids or full URLs, turn one metric into
millions of files and a dashboard nobody can query.

Bound the values before they reach a name:

```python
import statsd

routes = statsd.Counter('app.routes')


def record(route_template):
    # 'users/{id}' is one series. 'users/12345' is one series per user.
    routes.increment(route_template.replace('/', '_'))


record('users/{id}')
record('orders/{id}/items')
```

Note the substitution: a dot in a path segment becomes a new level in the
Graphite tree, and a slash is not valid in a name at all. Whatever scheme
you pick, apply it in one place rather than at each call site.

## A client per class

```python
import statsd

connection = statsd.Connection(host='statsd-1', port=8125)
app_client = statsd.Client(__name__, connection)


class Report:
    def __init__(self):
        self.statsd_client = app_client.get_client(type(self).__name__)

    def generate(self):
        timer = self.statsd_client.get_client(class_=statsd.Timer)
        timer.start()
        # fetch the rows
        timer.intermediate('fetch')
        # render the output
        timer.stop('total')


Report().generate()
```

Every class gets a namespace under the module name, and the timer inherits
it. Nothing inside `generate` mentions where the metric ends up.

Sub-clients share their parent's connection, which is the expensive part:

```python
import statsd

connection = statsd.Connection(host='statsd-1', port=8125)
root = statsd.Client('app', connection)

assert root.get_client('database').connection is connection
```

So a per-request client is cheap. A per-request `Connection` is a new
socket every request, and that one is worth avoiding.

## Django

Use [django-statsd](https://github.com/wolph/django-statsd), the sister
project built on this client. It ships middleware that times every view
and reports the database queries per request, which is the integration
most people want and nobody enjoys writing twice.

```bash
pip install django-statsd
```

Its README has the current settings. The short version is that it adds
middleware, and the metric names follow the view names.

## WSGI

Without a framework, a middleware is a function that wraps another
callable. This one times every request and counts the responses by status
class:

```python
import statsd

metrics = statsd.Client('app.http')
requests = metrics.get_counter('responses')
latency = metrics.get_timer('latency')


def statsd_middleware(application):
    def middleware(environ, start_response):
        timer = latency.get_client(class_=statsd.Timer)
        timer.start()

        def record(status, headers, *args):
            requests.increment(f'{status[0]}xx')
            return start_response(status, headers, *args)

        try:
            return application(environ, record)
        finally:
            timer.stop(environ.get('PATH_INFO', '/').strip('/') or 'root')

    return middleware


def hello(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b'hello']


application = statsd_middleware(hello)
application({'PATH_INFO': '/health'}, lambda status, headers: None)
```

That records `app.http.responses.2xx` and `app.http.latency.health`. The
timing goes in a `finally` block for the same reason the context manager
sends on exceptions: a request that blew up is the one you want in the
graph.

Note the path segment. Taking `PATH_INFO` straight from the request is the
cardinality mistake from earlier, so map paths to route templates before
they become names.

## Celery

Celery's signals give you the hooks without touching task code. This block
needs Celery installed, so the test suite does not run it:

<!-- docs-example: skip -->
```python
import statsd
from celery import signals

tasks = statsd.Client('app.tasks')
timers = {}


@signals.task_prerun.connect
def start_timer(task_id, task, **kwargs):
    timer = tasks.get_client(task.name.replace('.', '_'), statsd.Timer)
    timers[task_id] = timer.start()


@signals.task_postrun.connect
def stop_timer(task_id, task, state, **kwargs):
    timer = timers.pop(task_id, None)
    if timer is not None:
        timer.stop(state.lower())


@signals.task_failure.connect
def count_failure(task_id, **kwargs):
    tasks.get_counter('failures').increment()
```

The dictionary is there because the signals are separate calls, and a task
id is the only thing that connects them. Clear it in `task_postrun` rather
than letting a failed task leak an entry, which the `pop` above does.

## Production notes

My rule of thumb is the same one the connections page states: a counter
incremented on every request is a fine candidate for `sample_rate=0.1`, and
a counter for failed payments is not. At one failure an hour, sampling
means you hear about one of them per day.

Give each deployment its own prefix if several share a statsd server. A
client named for the environment at the root (`prod.app`, `staging.app`)
costs one extra segment and saves you reading two environments as one
graph.

Keep the flush interval in mind when reading a graph. The server
aggregates over its interval, commonly ten seconds, so a spike shorter
than that shows up averaged with its neighbours. When a burst matters more
than the average, count it as well as timing it.
