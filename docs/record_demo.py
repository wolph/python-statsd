r"""Record the README terminal demo as an asciicast.

Runs ``docs/demo.sh`` under a pty and writes every chunk the terminal
emits, with the time it was emitted, in asciicast v2 format. The result is
a recording of a real session: every command in the script runs for real,
and the ``udp :8125 <`` lines are packets ``examples/udp_listener.py``
actually received. The demo script types each command out before running
it, so the pace is chosen, and what you see run is what ran.

    uv run python docs/record_demo.py
    agg --theme monokai --font-size 18 --idle-time-limit 1.2 \\
        --last-frame-duration 2 docs/_static/demo.cast docs/_static/demo.gif

asciinema itself is not used here: run outside a terminal it buffers the
whole session and writes it as one event, which renders as a GIF with
three frames.
"""

import argparse
import json
import os
import pathlib
import pty
import select
import time

COLUMNS = 92
ROWS = 22


def parse_args() -> argparse.Namespace:
    """Read the tape and output paths from the CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--script',
        type=pathlib.Path,
        default=pathlib.Path('docs/demo.sh'),
        help='shell script to record (default: %(default)s)',
    )
    parser.add_argument(
        '--output',
        type=pathlib.Path,
        default=pathlib.Path('docs/_static/demo.cast'),
        help='asciicast file to write (default: %(default)s)',
    )
    return parser.parse_args()


def record(
    command: list[str], columns: int, rows: int
) -> list[tuple[float, str]]:
    """Run `command` under a pty, returning (offset, output) pairs."""
    pid, master = pty.fork()
    if pid == 0:  # pragma: no cover - this branch execs and never returns
        os.environ['COLUMNS'] = str(columns)
        os.environ['LINES'] = str(rows)
        os.environ['TERM'] = 'xterm-256color'
        os.execvp(command[0], command)

    events: list[tuple[float, str]] = []
    start = time.monotonic()
    while True:
        ready, _, _ = select.select([master], [], [], 30)
        if not ready:
            break
        try:
            chunk = os.read(master, 8192)
        except OSError:
            break
        if not chunk:
            break
        events.append(
            (time.monotonic() - start, chunk.decode('utf-8', 'replace'))
        )

    os.close(master)
    os.waitpid(pid, 0)
    return events


def write_cast(
    path: pathlib.Path,
    events: list[tuple[float, str]],
    columns: int,
    rows: int,
) -> None:
    """Write the events out as an asciicast v2 file."""
    header = {
        'version': 2,
        'width': columns,
        'height': rows,
        'timestamp': int(time.time()),
        'env': {'TERM': 'xterm-256color', 'SHELL': '/bin/bash'},
    }
    with path.open('w') as cast:
        cast.write(json.dumps(header) + '\n')
        for offset, data in events:
            cast.write(json.dumps([round(offset, 3), 'o', data]) + '\n')


def main() -> None:
    """Record the demo and report what landed."""
    args = parse_args()
    events = record(['bash', str(args.script)], COLUMNS, ROWS)
    write_cast(args.output, events, COLUMNS, ROWS)

    duration = events[-1][0] if events else 0.0
    print(f'{len(events)} events over {duration:.1f}s -> {args.output}')


if __name__ == '__main__':
    main()
