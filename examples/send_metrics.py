"""Feed the local stack with metrics that look like a small web service.

Bring the stack up first, then run this for a couple of minutes so carbon
has something to draw:

    docker compose up -d
    uv run python examples/send_metrics.py --seconds 120

Every metric here goes through the same public API the documentation uses,
so what lands in Graphite is exactly what your own code would produce.
"""

import argparse
import random
import time

import statsd


def parse_args() -> argparse.Namespace:
    """Read the run length and the statsd destination from the CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--seconds',
        type=int,
        default=120,
        help='how long to keep sending (default: %(default)s)',
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='statsd host (default: %(default)s)',
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8125,
        help='statsd port (default: %(default)s)',
    )
    return parser.parse_args()


def send_request(
    requests: statsd.Counter,
    render: statsd.Timer,
    errors: statsd.Counter,
) -> None:
    """Simulate one request: count it, time it, sometimes fail it."""
    requests.increment()
    with render.time('page'):
        # A log-normal-ish spread gives a p95 worth looking at, rather
        # than the flat line a uniform random walk draws.
        time.sleep(min(random.lognormvariate(-4.0, 0.7), 0.4))

    if random.random() < 0.04:
        errors.increment()


def main() -> None:
    """Send traffic until the clock runs out."""
    args = parse_args()
    connection = statsd.Connection(host=args.host, port=args.port)

    app = statsd.Client('demo', connection)
    requests = app.get_counter('requests')
    errors = app.get_counter('errors')
    render = app.get_timer('render')
    queue = app.get_gauge('queue')

    deadline = time.monotonic() + args.seconds
    depth = 12

    while time.monotonic() < deadline:
        send_request(requests, render, errors)

        # A queue that wanders instead of jittering around one value.
        depth = max(0, min(60, depth + random.randint(-3, 3)))
        queue.send('depth', depth)

        time.sleep(random.uniform(0.05, 0.2))

    print(f'done after {args.seconds}s against {args.host}:{args.port}')


if __name__ == '__main__':
    main()
