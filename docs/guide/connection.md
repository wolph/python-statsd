# Connections

A {class}`~statsd.connection.Connection` is a UDP socket, a destination
and a sample rate. Every client holds one, and clients created with
{meth}`~statsd.client.Client.get_client` share their parent's, so an
application normally has one connection and many clients.

## Defaults

Create a client without a connection and it builds one from the
class-level defaults: `localhost`, port `8125`, sample rate `1`, enabled.
Change them once at startup and everything created afterwards follows:

```python
import statsd

statsd.Connection.set_defaults(
    host='localhost', port=8125, sample_rate=1, disabled=False
)
```

These are class attributes, so the call affects clients created after it,
not connections that already exist. Call it before the application
creates its clients, and treat it as startup configuration rather than a
runtime switch.

## Explicit connections

When one destination is not enough, build connections yourself and hand
them to the clients that need them:

```python
import statsd

metrics = statsd.Connection(host='statsd-1', port=8125)
slow_path = statsd.Connection(host='statsd-2', port=8125, sample_rate=0.1)

statsd.Counter('MyApplication.requests', metrics).increment()
statsd.Timer('MyApplication.render', slow_path).start()
```

## Sampling

A sample rate below 1 is a probability. The client rolls the dice per
send and, when a packet does go out, it carries the rate so the server
can multiply back up:

```python
import statsd

connection = statsd.Connection(sample_rate=0.5)
statsd.Counter('MyApplication.requests', connection).increment()
```

On the wire that is `MyApplication.requests:1|c|@0.5`, and the server
treats it as roughly two events. Sampling trades accuracy for packets, so
it belongs on high-frequency counters and timers, not on the rare events
where every one matters.

One sharp edge: a falsy argument means "use the default", not "use zero".
`Connection(sample_rate=0)` gets you a sample rate of 1 and full traffic,
and the same rule applies to `host`, `port` and `disabled`. To send
nothing, disable the connection.

## Turning it off

```python
import statsd

connection = statsd.Connection(
    host='statsd-1', port=8125, sample_rate=0.5, disabled=True
)
statsd.Counter('MyApplication.requests', connection).increment()
```

A disabled connection builds its socket and then never writes to it. The
client API stays identical, so this is the switch to use for test suites
and for environments with no statsd server, rather than wrapping every
call site in a condition.

## Failure and logging

Sends never raise. An {exc}`OSError` from the socket is logged with a
traceback and reported as a failed send, and every other exception is
left to propagate, because a `TypeError` in your own metric name is a bug
worth seeing rather than a packet worth dropping.

Each connection logs to `statsd.connection.Connection`, at debug level
for setup and for suppressed sends. To see what a disabled connection is
not sending:

```python
import logging

import statsd

logging.basicConfig(level=logging.DEBUG)
connection = statsd.Connection(disabled=True)
statsd.Counter('MyApplication.requests', connection).increment()
```
