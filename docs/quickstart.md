# Quickstart

Two ways in. The first needs nothing but Python and proves your metrics
are real by printing the bytes. The second brings up statsd, Graphite and
Grafana so you can watch them turn into graphs.

## One minute, no Docker

**1. Install.**

```bash
pip install python-statsd
```

**2. Listen on the statsd port.** In one terminal, from a checkout of this
repository:

```bash
uv run python examples/udp_listener.py
```

No checkout to hand? `ncat -ul 8125` does the same job.

**3. Send something.** In another terminal:

```python
import statsd

counter = statsd.Counter('app')
counter.increment('requests')

gauge = statsd.Gauge('app')
gauge.send('queue_depth', 42)

with statsd.Timer('app').time('render'):
    pass  # the work you are measuring
```

**4. Read the first terminal.** Three packets, one per metric:

```text
udp :8125 < app.requests:1|c
udp :8125 < app.queue_depth:42|g
udp :8125 < app.render:0.00112504|ms
```

That is the whole protocol. A name, a value, a type suffix, one UDP packet
each, and nothing sent back. The timing is in milliseconds, and an empty
block really does take about a microsecond. The
[metrics page](metrics.md) has the full table of what each type writes.

## Five minutes, with graphs

**1. Start the stack.** From a checkout:

```bash
docker compose up -d --wait
```

`--wait` returns when statsd, Graphite and Grafana all report healthy,
which takes a minute or so on a cold pull.

**2. Generate some traffic.**

```bash
uv run python examples/send_metrics.py --seconds 120
```

Or, with no local Python at all:

```bash
docker compose --profile demo up -d --wait
```

**3. Open <http://localhost:3000>.** Grafana has the datasource configured
and a dashboard loaded, and there is no login prompt. Give it ten seconds
to fill: statsd aggregates on a ten-second flush, so nothing appears
before the first one.

```{image} _static/grafana.png
:alt: Grafana showing request rate, render percentiles and queue depth
:width: 100%
```

**4. Point your own code at it.**

```python
import statsd

connection = statsd.Connection(host='localhost', port=8125)
requests = statsd.Counter('myapp', connection)
requests.increment('hits')
```

Your metric shows up in Graphite as
`stats.counters.myapp.hits.rate`. statsd renames things on the way
through, and the [local stack page](local-stack.md) has the mapping table.

**5. Already have a Grafana?** The dashboard and the datasource and
provider files are in the repository, ready to lift into it. The
[local stack page](local-stack.md) lists each one with an import URL.

**6. Stop it when you are done.**

```bash
docker compose down
```

Add `-v` to throw away the stored metrics as well.

## Testing your own code

Metrics tend to be the part of a codebase nobody tests, because a real
server is a nuisance in a test suite. Two ways around that.

Disable the connection, and every call becomes a no-op while the API stays
identical:

```python
import statsd

connection = statsd.Connection(disabled=True)
counter = statsd.Counter('app', connection)
counter.increment('requests')
```

Or replace the socket and assert on what was sent, which is what this
library's own test suite does:

```python
from unittest import mock

import statsd

with mock.patch('socket.socket') as socket_class:
    statsd.Counter('app').increment('requests')

sent = [call.args[0] for call in socket_class.return_value.send.call_args_list]
assert sent == [b'app.requests:1|c']
```

That assertion is the real payload, not a paraphrase of one. Copy the
pattern and your tests fail when a metric name changes, which is usually
the moment you want to hear about it.

## Where to go next

- [Metrics](metrics.md): the five types, how to choose, and the bytes each
  one writes
- [Connections](connections.md): destinations, sampling, disabling,
  failure behaviour
- [Patterns](patterns.md): naming, client trees, framework integration
- [Local stack](local-stack.md): the compose stack in detail, and what to
  check when nothing arrives
