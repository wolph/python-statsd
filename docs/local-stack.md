# A local stack

Reading about metrics is not the same as watching one arrive. The
repository ships a `docker-compose.yml` that brings up statsd, Graphite
and Grafana, so you can send a counter and see it in a graph a few seconds
later.

## Up and running

```bash
docker compose up -d
uv run python examples/send_metrics.py --seconds 120
```

Then open <http://localhost:3000>. Grafana comes up with the Graphite
datasource already configured and a dashboard already loaded, with no
login prompt in the way. Graphite's own interface is on
<http://localhost:8080> if you want to browse the metric tree.

The feeder script sends what a small web service would: a request counter,
an error counter, a timer around the rendering, and a gauge that wanders
like a queue. Every call goes through the same public API the rest of
these pages use.

Ports are overridable, which matters if something already owns 8125 or
3000 on your machine:

```bash
GRAFANA_PORT=3001 STATSD_PORT=18125 GRAPHITE_HTTP_PORT=8081 docker compose up -d
```

When you are done:

```bash
docker compose down -v
```

The `-v` throws away the whisper files as well, so the next run starts
from an empty tree.

## Pointing your own code at it

Nothing special, because the stack listens on the default statsd port:

```python
import statsd

connection = statsd.Connection(host='localhost', port=8125)
statsd.Counter('myapp', connection).increment('requests')
```

Give it ten seconds. statsd flushes on an interval, this compose file sets
it to ten seconds, and until that flush happens Graphite has nothing to
draw.

## Where your metrics land

statsd rewrites the names on the way through, and knowing the mapping
saves a confused half hour in the Graphite tree. The compose file runs the
default configuration, which is the legacy namespace:

| You send | Graphite stores |
| --- | --- |
| `demo.requests:1\|c` | `stats.demo.requests` (per second) and `stats_counts.demo.requests` (total) |
| `demo.render:12.4\|ms` | `stats.timers.demo.render.{mean,upper_90,upper,count,...}` |
| `demo.depth:18\|g` | `stats.gauges.demo.depth` |

So a counter you send as `demo.requests` is queried as
`stats.demo.requests`, and the timer you sent once arrives as a family of
series, one per statistic the server computed.

statsd also reports on itself. `stats.statsd.packets_received` is the
first thing to look at when your own metrics are missing, because it
separates "nothing arrived" from "something arrived and I am querying the
wrong name".

## When nothing shows up

Work outwards from your process.

Is the client sending at all? Turn on debug logging, which is covered at
the end of the [connections page](connections.md).

Is anything on the wire? Listen on the port yourself, with the stack
stopped:

```bash
ncat -ul 8125
```

Then run your code. The payloads appear as plain text, one per packet,
exactly as the wire-format table on the [metrics page](metrics.md)
describes them. No `ncat` to hand:

```bash
sudo tcpdump -i lo0 -A 'udp port 8125'
```

Is statsd receiving? Its admin interface answers on port 8126:

```bash
echo counters | nc localhost 8126
```

Is Graphite storing? Ask the render API directly, which returns JSON and
skips the browser entirely:

```bash
curl 'http://localhost:8080/render?target=stats.demo.requests&from=-10min&format=json'
```

An empty list means the series does not exist, so the name is wrong or
nothing ever arrived. A series of `null` datapoints means the series
exists and the window you asked for is empty, which usually means you are
looking at a gap rather than a failure.

## A note for Apple Silicon

`graphiteapp/graphite-statsd` publishes amd64 images, so on an M-series
Mac the container runs under emulation. It works, and it is slower to
start than you might expect. Give it a minute before deciding something is
broken.
