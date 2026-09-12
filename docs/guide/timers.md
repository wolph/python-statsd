# Timers

A timer answers "how long did this take?", and the statsd server turns the
stream of durations into a mean, a median and percentiles. Measurements
use {func}`time.perf_counter`, so a clock adjustment in the middle of a
measurement cannot produce a negative duration.

## Explicit start and stop

```python
import statsd

timer = statsd.Timer('MyApplication')
timer.start()
# the work you are measuring
timer.stop('SomeTimer')
```

That sends `MyApplication.SomeTimer`. `start()` returns the timer, so it
chains if you prefer a single expression.

## As a context manager

```python
import statsd

with statsd.Timer('MyApplication').time('SomeTimer'):
    pass  # the work you are measuring
```

The metric is sent when the block ends, including when the block raises.
A timing that only records successes hides exactly the slow path you went
looking for, which is why the exception case sends too rather than
swallowing the measurement.

The context manager yields a timer, so intermediate marks are available
inside the block:

```python
import statsd

with statsd.Timer('MyApplication').time('total') as timer:
    timer.intermediate('parsed')
    timer.intermediate('validated')
```

Watch the names here. `time('total')` hands you a sub-client named
`MyApplication.total`, so the marks land under it as
`MyApplication.total.parsed` and `MyApplication.total.validated`, and the
block's own duration arrives as `MyApplication.total` at the end. If you
want the marks as siblings rather than children, drive the timer
explicitly instead, as in the section below.

## As a decorator

```python
import statsd

timer = statsd.Timer('MyApplication')


@timer.decorate
def some_function():
    pass
```

Calling `some_function()` sends `MyApplication.some_function`. The
function name becomes the metric name, which keeps the two from drifting
apart when the function is renamed.

Pass a name to choose it yourself:

```python
import statsd

timer = statsd.Timer('MyApplication')


@timer.decorate('custom_name')
def some_function():
    pass
```

## Intermediate measurements

`intermediate()` sends the time since the previous mark and leaves the
timer running, so a single pass through a pipeline reports each stage
separately:

```python
import statsd

timer = statsd.Timer('MyApplication')
timer.start()
timer.intermediate('fetch')
timer.intermediate('parse')
timer.stop('total')
```

`total` covers the whole run, and `fetch` and `parse` cover their own
stages.

## Misuse raises

Stopping a timer that was never started, or starting one twice, raises
{exc}`RuntimeError`:

```python
import statsd

timer = statsd.Timer('MyApplication')
try:
    timer.stop('SomeTimer')
except RuntimeError as exception:
    print(exception)
```

Before 3.0.0 these were {exc}`AssertionError`, which meant `python -O`
silently removed the check and reported a nonsense duration instead.
