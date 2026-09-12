# Counters

A counter reports a delta, not a level. The server adds up everything it
receives during a flush interval and reports the sum, which is what makes
counters the right tool for "how often" questions: requests served, cache
misses, retries.

## Incrementing

```python
import statsd

counter = statsd.Counter('MyApplication')
counter.increment('requests')
counter.increment('requests', 10)
```

The first call sends a delta of 1 to `MyApplication.requests`, the second
a delta of 10 to the same metric.

Operators do the same thing without a sub-name, which reads well when the
client is already named for the thing being counted:

```python
import statsd

requests = statsd.Counter('MyApplication.requests')
requests += 1
requests -= 1
```

`+=` and `-=` return the counter, so the name stays bound to the same
object. Nothing accumulates client-side: each operator is one UDP packet
carrying that delta.

## Decrementing

```python
import statsd

counter = statsd.Counter('MyApplication')
counter.decrement('queue_depth')
counter.decrement('queue_depth', 5)
```

A decrement is a negative delta. If what you actually want is the current
level rather than a running sum, use a [gauge](gauges.md) instead, because
a counter that is incremented and decremented in equal measure reports
zero rather than the level you were after.

## One-shot helpers

For a counter you touch once and never hold onto, the module-level
helpers save the intermediate variable:

```python
import statsd

statsd.increment('MyApplication.requests')
statsd.decrement('MyApplication.queue_depth', 5)
```

Each call builds a `Counter` on the default connection, sends, and
discards it. That is one socket per call, so prefer a long-lived client
on a hot path and keep these for the occasional event.

## Sub-clients

`get_client()` appends to the name, which keeps related counters together
without repeating the prefix:

```python
import statsd

app = statsd.Counter('MyApplication')
cache = app.get_client('cache')

cache.increment('hit')
cache.increment('miss')
```

That sends `MyApplication.cache.hit` and `MyApplication.cache.miss`.
