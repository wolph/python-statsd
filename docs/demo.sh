#!/usr/bin/env bash
#
# The session recorded for the README GIF. Each command is typed out and
# then run, so the pace is chosen and the output is not: every line under
# "udp :8125 <" is a packet examples/udp_listener.py received on a real
# socket.
#
# Re-record from the project root with:
#     uv run python docs/record_demo.py
#     agg --theme monokai --font-size 18 --idle-time-limit 1.2 \
#         --last-frame-duration 2 docs/_static/demo.cast docs/_static/demo.gif

set -u

PROMPT=$'\033[1;32m$\033[0m '
COMMENT=$'\033[38;5;245m'
RESET=$'\033[0m'

type_out() {
    printf '%s' "$PROMPT"
    local line="$1"
    for ((i = 0; i < ${#line}; i++)); do
        printf '%s' "${line:i:1}"
        sleep 0.022
    done
    printf '\n'
    sleep 0.3
}

run() {
    type_out "$1"
    eval "$1"
    sleep 1.0
}

say() {
    printf '%s# %s%s\n' "$COMMENT" "$1" "$RESET"
    sleep 0.45
}

clear
say 'listen on the statsd port, so we can see what goes out'
run "uv run python examples/udp_listener.py &"
sleep 1.5

say 'count something'
run "uv run python -c \"import statsd; statsd.Counter('app').increment('requests')\""

say 'report a level'
run "uv run python -c \"import statsd; statsd.Gauge('app').send('queue_depth', 42)\""

say 'time a block, including when it raises'
run "uv run python -c \"
import statsd, time
with statsd.Timer('app').time('render'):
    time.sleep(0.05)
\""

say 'sample a busy counter at 50%'
run "uv run python -c \"
import statsd
conn = statsd.Connection(sample_rate=0.5)
for _ in range(4):
    statsd.Counter('app', conn).increment('hits')
\""

sleep 1.2
kill %1 2>/dev/null
wait 2>/dev/null
