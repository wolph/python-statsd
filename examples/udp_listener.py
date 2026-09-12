"""Print every statsd packet that arrives, one line per packet.

Handy when metrics are not showing up and you want to know whether the
client is sending anything at all:

    uv run python examples/udp_listener.py

It binds the statsd port itself, so stop your statsd server first or give
this a different port with --port.
"""

import argparse
import socket


def parse_args() -> argparse.Namespace:
    """Read the bind address from the CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8125)
    parser.add_argument(
        '--prefix',
        default='udp :8125 <',
        help='printed in front of every packet (default: %(default)s)',
    )
    return parser.parse_args()


def main() -> None:
    """Bind the port and print packets until interrupted."""
    args = parse_args()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.host, args.port))

    try:
        while True:
            payload, _ = sock.recvfrom(8192)
            print(f'{args.prefix} {payload.decode()}', flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()


if __name__ == '__main__':
    main()
