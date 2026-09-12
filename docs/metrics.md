# Metrics

Five metric types, and the whole skill is picking the right one. The
question that separates them is not what you are measuring, it is what you
want the server to do with a burst of values that arrive inside a single
flush interval.

| Type | A burst of values becomes | Reach for it when |
| --- | --- | --- |
| `Counter` | their sum | you are counting events |
| `Gauge` | the last one | you are reporting a level |
| `Timer` | mean, median, percentiles | you are measuring duration |
| `Average` | their mean | the server should average samples |
| `Raw` | stored as sent | you already did the summarising |

`Counter` and `Timer` cover almost everything. The other three earn their
place on specific days, and the sections below say which days those are.

## Counters

A counter sends a delta. The server adds the deltas up over the flush
interval and reports the total, which is why a counter answers "how often"
and never "how many right now".

```python
import statsd

counter = statsd.Counter('app')
counter.increment('requests')
counter.increment('requests', 10)
```

Those two calls put `app.requests:1|c` and `app.requests:10|c` on the
socket. The name splits in two: `app` comes from the client and `requests`
from the call, and statsd joins them with a dot.

The operators do the same job without a sub-name, which reads better when
the client is already named for the thing being counted:

```python
import statsd

requests = statsd.Counter('app.requests')
requests += 1
requests -= 2
```

That sends `app:1|c` and `app:-2|c` for a client named `app`. Nothing
accumulates on your side: each operator is one packet carrying that delta,
so a loop that increments a million times sends a million packets. When
that is a problem, sample it, which the [connections
page](connections.md) covers.

For a counter you touch once and never hold onto, the module-level
shortcuts skip the intermediate variable:

```python
import statsd

statsd.increment('app.requests')
statsd.decrement('app.queue', 5)
```

Each call builds a `Counter` on the default connection, sends, and throws
it away. That is a socket per call, so keep these for occasional events
and give a hot path a client of its own.

## Gauges

A gauge sends a level, and the server remembers the last value it saw.
Queue depth, pool size, free disk, temperature: anything where the current
reading is the answer and the history is somebody else's problem.

```python
import statsd

gauge = statsd.Gauge('app')
gauge.send('depth', 42)
gauge.send('load', 0.75)
```

That is `app.depth:42|g` and `app.load:0.75|g`. Values may be `int`,
`float` or `decimal.Decimal`.

Send a signed value and statsd adjusts the stored level instead of
replacing it. {meth}`~statsd.gauge.Gauge.increment` and
{meth}`~statsd.gauge.Gauge.decrement` send that form:

```python
import statsd

gauge = statsd.Gauge('app')
gauge.increment('depth')
gauge.decrement('depth', 3)
```

On the wire: `app.depth:+1|g` and `app.depth:-3|g`. Two things to know
before relying on them. The delta is cast to `int` on the way out, so a
fractional adjustment is truncated. And a relative update is only as good
as the value the server currently holds, which is nothing at all if the
server restarted since your last absolute send.

A non-numeric value raises instead of sending:

```python
import statsd

gauge = statsd.Gauge('app')
try:
    gauge.send('depth', 'forty two')
except TypeError as exception:
    print(exception)
```

That prints `gauge values must be numeric, got 'forty two'`. The
alternative is a packet the server accepts and files as nonsense, which
you discover a week later in a graph that has been flat since Tuesday.

## Timers

A timer measures a duration and lets the server compute the percentiles.
Measurements come from {func}`time.perf_counter`, so a clock adjustment
mid-measurement cannot hand you a negative duration.

```python
import statsd

timer = statsd.Timer('app')
timer.start()
# the work you are measuring
timer.stop('render')
```

That sends `app.render:0.00033295|ms`: milliseconds, eight decimal places,
computed on this side. The server needs the raw durations because the
percentiles have to be calculated over the whole population, not over your
process's view of it.

The context manager is the form to reach for, because it sends the metric
even when the block raises:

```python
import statsd

with statsd.Timer('app').time('render'):
    pass  # the work you are measuring
```

A timing that only records successes hides the slow path you went looking
for. The exception case is exactly the measurement worth having.

The decorator names the metric after the function:

```python
import statsd

timer = statsd.Timer('app')


@timer.decorate
def render_page():
    pass
```

Calling `render_page()` sends `app.render_page`. Rename the function and
the metric follows, which is one fewer string to keep in sync. Pass a name
to `decorate` when you want to choose it yourself. Be aware that the
decorator sees a function, not a class, so two classes with a `render`
method sharing one timer report into the same series.

`intermediate()` marks a stage and leaves the clock running:

```python
import statsd

timer = statsd.Timer('app')
timer.start()
timer.intermediate('fetch')
timer.intermediate('parse')
timer.stop('total')
```

That gives you `app.fetch`, `app.parse` and `app.total`, where `total`
covers the whole run and the other two cover their own stages.

Watch the names when combining the two forms. `time('total')` hands you a
sub-client called `app.total`, so a mark taken inside that block arrives
as `app.total.parsed`, a child rather than a sibling.

Misuse raises rather than reporting nonsense:

```python
import statsd

timer = statsd.Timer('app')
try:
    timer.stop('render')
except RuntimeError as exception:
    print(exception)
```

That prints `Unable to stop, the timer was never started`. Starting a
running timer raises the same way. Before 3.0.0 both were assertions,
which `python -O` removed, leaving a duration measured from nothing.

## Averages and raw values

Both of these hand the server a number you already computed, and both are
extensions rather than core statsd. Check your server speaks them before
building a dashboard on top: the reference implementation is
[chuyskywalker's fork](https://github.com/chuyskywalker/statsd/blob/master/README.md).

An average is combined with whatever else arrives in the interval:

```python
import statsd

average = statsd.Average('app')
average.send('batch', 123)
```

That sends `app.batch:123|a`. Values go out as integers, so scale before
sending when the decimal matters.

A raw value is passed through to carbon with a timestamp and no
aggregation at all:

```python
import statsd

raw = statsd.Raw('app')
raw.send('summary', 42, timestamp=1234567890)
```

That sends `app.summary:42|r|1234567890`. The timestamp is seconds since
the epoch, the same number `date +%s` prints. Leave it out and the current
time is used.

Raw is a bandwidth argument as much as a semantic one. A gauge sampled a
thousand times a second costs a thousand packets whose UDP headers dwarf
their payloads. The same series summarised in your own process and sent
once costs one.

So: several workers reporting their own summaries into one series want
`Average`, and a single authoritative reading wants `Raw`.

## The wire format

Every payload above, in one place. These are the exact bytes this client
writes to the socket, read back from the fake socket the test suite
installs.

| Call | Payload |
| --- | --- |
| `Counter('app').increment('requests')` | `app.requests:1\|c` |
| `Counter('app').increment('requests', 10)` | `app.requests:10\|c` |
| `Counter('app').decrement('queue', 3)` | `app.queue:-3\|c` |
| `Gauge('app').send('depth', 42)` | `app.depth:42\|g` |
| `Gauge('app').increment('depth')` | `app.depth:+1\|g` |
| `Gauge('app').decrement('depth', 3)` | `app.depth:-3\|g` |
| `Timer('app')` start then `stop('render')` | `app.render:0.00033295\|ms` |
| `Average('app').send('batch', 123)` | `app.batch:123\|a` |
| `Raw('app').send('summary', 42, timestamp=1234567890)` | `app.summary:42\|r\|1234567890` |
| any of the above under `sample_rate=0.5` | the same, plus `\|@0.5` |

One packet per metric, one metric per packet, no batching. The suffix
after the second pipe is the type: `c` counter, `g` gauge, `ms` timer,
`a` average, `r` raw.

Nothing here is a guess. If a payload above ever stops matching what the
code sends, the table is wrong and worth reporting as a bug.
