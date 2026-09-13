# A local stack

Reading about metrics is not the same as watching one arrive. The
repository ships a `docker-compose.yml` that brings up statsd, Graphite
and Grafana, so you can send a counter and see it in a graph ten seconds
later.

## Up and running

```bash
docker compose up -d --wait
uv run python examples/send_metrics.py --seconds 120
```

`--wait` holds until every service reports healthy, so when the command
returns the stack is actually ready rather than merely started. Then open
<http://localhost:3000>: Grafana has the Graphite datasource configured
and a dashboard loaded, with no login prompt in the way.

The feeder script sends what a small web service would: a request counter,
an error counter, a timer around the rendering, and a gauge that wanders
like a queue. Every call goes through the same public API the rest of
these pages use, so nothing in the graphs comes from anywhere special.

No Python to hand? The stack can generate its own traffic:

```bash
docker compose --profile demo up -d --wait
```

That runs the same script in a container against the `statsd` service,
installing `python-statsd` from PyPI as it starts. `DEMO_SECONDS` sets how
long it keeps going, an hour by default.

## What is in the stack

| Service | Image | Port | Job |
| --- | --- | --- | --- |
| `statsd` | `statsd/statsd` | 8125/udp, 8126 | Aggregates your packets, flushes every 10s |
| `graphite` | `graphiteapp/graphite-statsd` | 8080 | carbon stores the series, graphite-web queries them |
| `grafana` | `grafana/grafana` | 3000 | Draws them |
| `demo` | `python:3.13-slim` | none | Optional traffic generator, `--profile demo` |

The statsd service is the real thing from
[statsd/statsd](https://github.com/statsd/statsd), reading
`examples/statsd/config.js` from this repository. The Graphite image
bundles a statsd of its own, which this stack leaves unused, because the
point is to show you the configuration your packets actually meet.

Every image here is published for amd64 and arm64, so an Apple Silicon
machine runs the stack natively rather than under emulation.

## The statsd configuration

`examples/statsd/config.js` is short enough to read in full, and three
settings shape what you see in the graphs:

```js
flushInterval: 10000,
graphite: { legacyNamespace: false },
percentThreshold: [50, 90, 95, 99],
```

`flushInterval` is how often statsd aggregates and forwards. Ten seconds
here, a minute by default, and whatever it is, a spike shorter than that
arrives averaged with its neighbours.

`legacyNamespace: false` picks the modern metric layout, which is the one
in the table below. The legacy layout puts counter rates at
`stats.<name>` instead, which is shorter to type and harder to explain.

`percentThreshold` decides which percentiles exist. Each one becomes its
own series, so `upper_90` is the p90 of whatever you timed.

## Where your metrics land

statsd rewrites names on the way through, and knowing the mapping saves a
confused half hour in the Graphite tree:

| You send | Graphite stores |
| --- | --- |
| `demo.requests:1\|c` | `stats.counters.demo.requests.rate` (per second) and `.count` (per flush) |
| `demo.render:12.4\|ms` | `stats.timers.demo.render.{mean,median,upper_90,upper_99,upper,count,...}` |
| `demo.depth:18\|g` | `stats.gauges.demo.depth` |

So one timer arrives as a family of series, one per statistic statsd
computed, and a counter arrives twice: as a rate and as a count.

statsd also reports on itself. `stats.counters.statsd.packets_received.count`
is the first thing to look at when your own metrics are missing, because
it separates "nothing arrived" from "something arrived and I am querying
the wrong name".

## Pointing your own code at it

Nothing special, because the stack listens on the default statsd port:

```python
import statsd

connection = statsd.Connection(host='localhost', port=8125)
statsd.Counter('myapp', connection).increment('requests')
```

Give it ten seconds. Until statsd flushes, Graphite has nothing to draw.

## Ports, data and cleaning up

Every published port is overridable, which matters when something already
owns 8125 or 3000 on your machine:

```bash
GRAFANA_PORT=3001 STATSD_PORT=18125 GRAPHITE_HTTP_PORT=8081 docker compose up -d --wait
```

Graphite's whisper files and Grafana's database live in named volumes, so
a `docker compose down` keeps your history and a restart picks it up
again. To throw it all away:

```bash
docker compose down -v
```

## When nothing shows up

Work outwards from your own process.

**Is the client sending at all?** Turn on debug logging, which the
[connections page](connections.md) covers at the end.

**Is anything on the wire?** Listen on the port yourself, with the stack
stopped:

```bash
uv run python examples/udp_listener.py
```

Then run your code. Every payload appears as plain text, one per packet,
exactly as the wire-format table on the [metrics page](metrics.md)
describes. `ncat -ul 8125` does the same job if you would rather not run
Python for it.

**Is statsd receiving?** Its admin interface answers on 8126:

```bash
echo counters | nc localhost 8126
```

That lists every counter statsd currently holds, which tells you whether
your name arrived the way you think it did.

**Is Graphite storing?** Ask the render API directly and skip the browser:

```bash
curl 'http://localhost:8080/render?target=stats.counters.demo.requests.rate&from=-10min&format=json'
```

An empty list means the series does not exist, so the name is wrong or
nothing ever arrived. A series of `null` datapoints means the series
exists and the window you asked for is empty, which is usually a gap
rather than a failure.

**Is a service unhealthy?** Every service has a healthcheck, so the state
is visible without reading logs:

```bash
docker compose ps
docker compose logs statsd --tail 20
```
