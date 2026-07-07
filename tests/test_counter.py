from unittest import mock

import pytest
import statsd


@pytest.fixture
def counter() -> statsd.Counter:
    return statsd.Counter('testing')


def last_sent(udp_socket: mock.MagicMock) -> bytes:
    return udp_socket.send.call_args[0][0]


def test_increment(
    counter: statsd.Counter, udp_socket: mock.MagicMock
) -> None:
    assert counter.increment('spam') is True
    assert last_sent(udp_socket) == b'testing.spam:1|c'


def test_increment_delta(
    counter: statsd.Counter, udp_socket: mock.MagicMock
) -> None:
    assert counter.increment('spam', 10) is True
    assert last_sent(udp_socket) == b'testing.spam:10|c'


def test_increment_no_subname(
    counter: statsd.Counter, udp_socket: mock.MagicMock
) -> None:
    assert counter.increment(delta=2) is True
    assert last_sent(udp_socket) == b'testing:2|c'


def test_decrement(
    counter: statsd.Counter, udp_socket: mock.MagicMock
) -> None:
    assert counter.decrement('spam') is True
    assert last_sent(udp_socket) == b'testing.spam:-1|c'


def test_decrement_delta(
    counter: statsd.Counter, udp_socket: mock.MagicMock
) -> None:
    assert counter.decrement('spam', 10) is True
    assert last_sent(udp_socket) == b'testing.spam:-10|c'


def test_add_returns_counter(
    counter: statsd.Counter, udp_socket: mock.MagicMock
) -> None:
    counter += 5
    assert isinstance(counter, statsd.Counter)
    assert last_sent(udp_socket) == b'testing:5|c'


def test_sub_returns_counter(
    counter: statsd.Counter, udp_socket: mock.MagicMock
) -> None:
    counter -= 5
    assert isinstance(counter, statsd.Counter)
    assert last_sent(udp_socket) == b'testing:-5|c'


def test_float_delta_truncates(
    counter: statsd.Counter, udp_socket: mock.MagicMock
) -> None:
    assert counter.increment('spam', 2.9) is True
    assert last_sent(udp_socket) == b'testing.spam:2|c'


def test_module_increment(udp_socket: mock.MagicMock) -> None:
    assert statsd.increment('spam') is True
    assert last_sent(udp_socket) == b'spam:1|c'
    assert statsd.increment('spam', 4) is True
    assert last_sent(udp_socket) == b'spam:4|c'


def test_module_decrement(udp_socket: mock.MagicMock) -> None:
    assert statsd.decrement('spam') is True
    assert last_sent(udp_socket) == b'spam:-1|c'
    assert statsd.decrement('spam', 4) is True
    assert last_sent(udp_socket) == b'spam:-4|c'
