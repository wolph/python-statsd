# Raw values and averages

These two types exist for data that has already been summarised
somewhere else. Both are extensions rather than core statsd features, so
check that your server speaks them before wiring them into a dashboard.
The reference is [chuyskywalker's statsd
fork](https://github.com/chuyskywalker/statsd/blob/master/README.md).

## Raw

A raw value skips aggregation entirely and is handed to carbon with a
timestamp attached:

```python
import statsd

raw = statsd.Raw('MyApplication')
raw.send('requests_per_minute', 42, timestamp=1234567890)
```

The timestamp is in seconds since the epoch, the same thing `date +%s`
prints. Leave it out and the current time is used:

```python
import statsd

raw = statsd.Raw('MyApplication')
raw.send('requests_per_minute', 42)
```

Raw is also a bandwidth argument, not only a semantic one. A gauge
sampled a thousand times a second costs a thousand UDP packets whose
headers dwarf their payloads, while the same series summarised in your
own process and sent once as a raw value costs one.

## Average

An average is aggregated by the server, which reports the mean of
everything it received in the flush interval:

```python
import statsd

average = statsd.Average('MyApplication')
average.send('batch_size', 123)
```

Values are sent as integers, so a mean you care about to the decimal
should be scaled before sending (microseconds instead of seconds, for
example) and scaled back in the graph.

## Choosing between them

Both types hand the server a number you already computed, and the
difference is what happens to a second number arriving in the same
interval. An average is combined with it, and a raw value is not: the
last one written wins. So a per-process summary that several workers send
at once wants `Average`, while a single authoritative reading wants
`Raw`.
