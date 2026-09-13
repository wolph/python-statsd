/*
 * statsd configuration for the local stack.
 *
 * This is the real thing: https://github.com/statsd/statsd reads this file
 * on startup. Everything below is deliberately explicit, so you can see
 * what shapes the numbers before they reach Graphite.
 */
{
  // Listen for the UDP packets this client sends.
  port: 8125,

  // Plain-text admin interface: `echo counters | nc localhost 8126`.
  mgmt_port: 8126,

  // Where the aggregates go. `graphite` is the compose service name, and
  // 2003 is carbon's plaintext receiver.
  graphiteHost: "graphite",
  graphitePort: 2003,

  // Aggregate over ten seconds rather than the default minute, so a graph
  // moves while you are still watching it. Production usually leaves this
  // at 10000 too, and the flush interval is what decides how coarse your
  // spikes look.
  flushInterval: 10000,

  graphite: {
    // Modern namespacing: counters land under stats.counters.<name>,
    // timers under stats.timers.<name>, gauges under stats.gauges.<name>.
    // The legacy layout puts counter rates at stats.<name> instead, which
    // is tidier to type and harder to explain.
    legacyNamespace: false,

    // Send the per-flush count as well as the rate.
    globalPrefix: "stats"
  },

  // Percentiles computed for every timer. Each one becomes its own series,
  // so `upper_90` is the p90 of whatever you timed.
  percentThreshold: [50, 90, 95, 99],

  // Keep flushing a metric as zero after traffic stops, rather than
  // dropping the series. Makes "did it stop, or did it break" answerable.
  deleteIdleStats: false,

  // Log every packet received. Useful while you are wiring things up,
  // noisy once it works.
  dumpMessages: false
}
