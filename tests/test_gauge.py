import decimal
from unittest import mock

import pytest
import statsd


@pytest.fixture
def gauge() -> statsd.Gauge:
    return statsd.Gauge('testing')


def last_sent(udp_socket: mock.MagicMock) -> bytes:
    return udp_socket.send.call_args[0][0]


def sent(udp_socket: mock.MagicMock) -> list[bytes]:
    return [call[0][0] for call in udp_socket.send.call_args_list]


def test_send_float(gauge: statsd.Gauge, udp_socket: mock.MagicMock) -> None:
    assert gauge.send('spam', 10.5) is True
    assert last_sent(udp_socket) == b'testing.spam:10.5|g'


def test_send_decimal(gauge: statsd.Gauge, udp_socket: mock.MagicMock) -> None:
    assert gauge.send('spam', decimal.Decimal('6.576')) is True
    assert last_sent(udp_socket) == b'testing.spam:6.576|g'


def test_send_integer(gauge: statsd.Gauge, udp_socket: mock.MagicMock) -> None:
    assert gauge.send('spam', 1) is True
    assert last_sent(udp_socket) == b'testing.spam:1|g'


def test_send_non_numeric_raises(gauge: statsd.Gauge) -> None:
    with pytest.raises(TypeError, match='numeric'):
        gauge.send('spam', 'not-a-number')  # type: ignore[arg-type]


def test_set_positive(gauge: statsd.Gauge, udp_socket: mock.MagicMock) -> None:
    assert gauge.set('spam', 1) is True
    assert sent(udp_socket) == [b'testing.spam:1|g']


def test_set_negative_sends_zero_first(
    gauge: statsd.Gauge, udp_socket: mock.MagicMock
) -> None:
    assert gauge.set('spam', -1) is True
    assert sent(udp_socket) == [b'testing.spam:0|g', b'testing.spam:-1|g']


def test_set_non_numeric_raises(gauge: statsd.Gauge) -> None:
    with pytest.raises(TypeError, match='numeric'):
        gauge.set('spam', None)  # type: ignore[arg-type]


def test_increment(gauge: statsd.Gauge, udp_socket: mock.MagicMock) -> None:
    assert gauge.increment('spam', 10) is True
    assert last_sent(udp_socket) == b'testing.spam:+10|g'
    assert gauge.increment(delta=10) is True
    assert last_sent(udp_socket) == b'testing:+10|g'


def test_increment_negative_delta(
    gauge: statsd.Gauge, udp_socket: mock.MagicMock
) -> None:
    assert gauge.increment('spam', -10) is True
    assert last_sent(udp_socket) == b'testing.spam:-10|g'


def test_decrement(gauge: statsd.Gauge, udp_socket: mock.MagicMock) -> None:
    assert gauge.decrement('spam', 10) is True
    assert last_sent(udp_socket) == b'testing.spam:-10|g'
    assert gauge.decrement(delta=10) is True
    assert last_sent(udp_socket) == b'testing:-10|g'


def test_decrement_negative_delta(
    gauge: statsd.Gauge, udp_socket: mock.MagicMock
) -> None:
    assert gauge.decrement('spam', -10) is True
    assert last_sent(udp_socket) == b'testing.spam:+10|g'


def test_add(gauge: statsd.Gauge, udp_socket: mock.MagicMock) -> None:
    gauge += 5
    assert isinstance(gauge, statsd.Gauge)
    assert last_sent(udp_socket) == b'testing:+5|g'


def test_sub(gauge: statsd.Gauge, udp_socket: mock.MagicMock) -> None:
    gauge -= 5
    assert isinstance(gauge, statsd.Gauge)
    assert last_sent(udp_socket) == b'testing:-5|g'
