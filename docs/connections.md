# Connections

A {class}`~statsd.connection.Connection` is a UDP socket, a destination
and a sample rate. Every client holds one, and every sub-client shares its
parent's, so an application normally ends up with one connection and many
clients.

## The defaults

Build a client without a connection and it makes one from the class-level
defaults: `localhost`, port `8125`, sample rate `1`, enabled. Change them
once at startup and everything built afterwards follows:

```python
import statsd

statsd.Connection.set_defaults(
    host='localhost', port=8125, sample_rate=1, disabled=False
)
```

These are class attributes, so the call reaches clients created after it
and leaves existing connections alone. Treat it as startup configuration,
not a runtime switch.

## Explicit connections

When one destination is not enough, build connections and hand them to the
clients that need them:

```python
import statsd

metrics = statsd.Connection(host='statsd-1', port=8125)
sampled = statsd.Connection(host='statsd-2', port=8125, sample_rate=0.1)

statsd.Counter('app.requests', metrics).increment()
statsd.Timer('app.render', sampled).start()
```

## Sampling

A sample rate below 1 is a probability. The client rolls once per send,
and a packet that does go out carries the rate so the server can multiply
back up:

```python
import statsd

connection = statsd.Connection(sample_rate=0.5)
statsd.Counter('app', connection).increment('requests')
```

That puts `app.requests:1|c|@0.5` on the wire, and the server reads it as
roughly two events. Sampling trades accuracy for packets, which suits
high-frequency counters and timers and ruins rare events, where every
single one matters and half of them are now gone.

Here is the sharp edge. A falsy argument means "use the default", not
"use zero":

```python
import statsd

print(statsd.Connection(sample_rate=0))
print(statsd.Connection(sample_rate=0.5))
```

That prints `<Connection[localhost:8125] P(1.0)>` and then
`<Connection[localhost:8125] P(0.5)>`. The zero became a 1, and the
connection sends everything. The same rule
applies to `host`, `port` and `disabled`, because each argument is read as
`value or default`. To send nothing, disable the connection rather than
reaching for a zero rate.

## Turning it off

```python
import statsd

connection = statsd.Connection(host='statsd-1', port=8125, disabled=True)
statsd.Counter('app.requests', connection).increment()
```

A disabled connection builds its socket and never writes to it. The client
API is unchanged, so this is the switch for test suites and for
environments with no statsd server, rather than wrapping call sites in
conditions.

## When things go wrong

Sends do not raise. An {exc}`OSError` from the socket is logged with a
traceback and reported as a failed send, and everything else propagates,
because a `TypeError` in your own metric name is a bug worth seeing rather
than a packet worth dropping.

```python
import statsd

connection = statsd.Connection(host='statsd.invalid')
counter = statsd.Counter('app', connection)
counter.increment('requests')
```

That runs cleanly on a machine where the host does not resolve. It is a
deliberate trade: a metrics client that can take your application down
with it is worse than no metrics.

Each connection logs to `statsd.connection.Connection`, at debug level for
setup and for sends a disabled connection swallowed:

```python
import logging

import statsd

logging.basicConfig(level=logging.DEBUG)
connection = statsd.Connection(disabled=True)
statsd.Counter('app.requests', connection).increment()
```

Turn that on when metrics are missing and you want to know whether the
client sent anything at all. It answers the client half of the question,
and the [local stack page](local-stack.md) answers the network half.

## Threads and forks

The socket is created once per connection and used with plain `send()`
calls, which are atomic for datagrams of this size. Threads sharing a
connection are fine: two threads sending at once produce two packets, not
one interleaved mess.

Forking is the case to think about. A child process inherits the parent's
socket file descriptor, which works, but both processes then send through
the same socket. That is harmless for UDP, where there is nothing to read
and no ordering to corrupt. What bites is a pre-fork server that builds
its connection before forking and then reconfigures it in the child: the
descriptor is shared, so you are configuring both. Build connections after
the fork, in the worker, and the question disappears.
