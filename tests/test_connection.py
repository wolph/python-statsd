from unittest import mock

import pytest
import statsd


@pytest.fixture
def connection() -> statsd.Connection:
    return statsd.Connection()


def sent(udp_socket: mock.MagicMock) -> list[bytes]:
    return [call[0][0] for call in udp_socket.send.call_args_list]


def test_defaults(connection: statsd.Connection) -> None:
    assert connection._host == 'localhost'
    assert connection._port == 8125
    assert connection._sample_rate == 1
    assert connection._disabled is False


def test_set_defaults_roundtrip() -> None:
    try:
        statsd.Connection.set_defaults('127.0.0.1', 1234, 0.5, True)
        connection = statsd.Connection()
        assert connection._host == '127.0.0.1'
        assert connection._port == 1234
        assert connection._sample_rate == 0.5
        assert connection._disabled is True
    finally:
        statsd.Connection.set_defaults()

    connection = statsd.Connection()
    assert connection._host == 'localhost'
    assert connection._port == 8125
    assert connection._sample_rate == 1
    assert connection._disabled is False


def test_send_writes_to_socket(
    connection: statsd.Connection, udp_socket: mock.MagicMock
) -> None:
    assert connection.send({'spam': '1|c'}) is True
    assert sent(udp_socket) == [b'spam:1|c']


def test_send_multiple_stats(
    connection: statsd.Connection, udp_socket: mock.MagicMock
) -> None:
    assert connection.send({'spam': '1|c', 'eggs': '2|c'}) is True
    assert sorted(sent(udp_socket)) == [b'eggs:2|c', b'spam:1|c']


def test_send_disabled(udp_socket: mock.MagicMock) -> None:
    connection = statsd.Connection(disabled=True)
    assert connection.send({'spam': '1|c'}) is False
    assert connection.send({'spam': '1|c'}, 1) is False
    assert not udp_socket.send.called


def test_send_sampled(
    connection: statsd.Connection, udp_socket: mock.MagicMock
) -> None:
    with mock.patch('random.random', return_value=0.4):
        assert connection.send({'spam': '1|c'}, sample_rate=0.5) is True
    assert sent(udp_socket) == [b'spam:1|c|@0.5']


def test_send_sampled_out(
    connection: statsd.Connection, udp_socket: mock.MagicMock
) -> None:
    with mock.patch('random.random', return_value=0.9):
        assert connection.send({'spam': '1|c'}, sample_rate=0.5) is True
    assert not udp_socket.send.called


def test_send_instance_sample_rate(udp_socket: mock.MagicMock) -> None:
    connection = statsd.Connection(sample_rate=0.5)
    with mock.patch('random.random', return_value=0.4):
        assert connection.send({'spam': '1|c'}) is True
    assert sent(udp_socket) == [b'spam:1|c|@0.5']


def test_send_socket_error_returns_false(
    connection: statsd.Connection, udp_socket: mock.MagicMock
) -> None:
    udp_socket.send.side_effect = OSError('no network')
    assert connection.send({'spam': '1|c'}) is False


def test_send_unexpected_error_propagates(
    connection: statsd.Connection, udp_socket: mock.MagicMock
) -> None:
    udp_socket.send.side_effect = ValueError('boom')
    with pytest.raises(ValueError, match='boom'):
        connection.send({'spam': '1|c'})


def test_del_closes_socket(udp_socket: mock.MagicMock) -> None:
    connection = statsd.Connection()
    connection.__del__()
    assert udp_socket.close.called


def test_del_without_socket() -> None:
    connection = statsd.Connection.__new__(statsd.Connection)
    connection.__del__()  # must not raise


def test_repr(connection: statsd.Connection) -> None:
    assert repr(connection) == '<Connection[localhost:8125] P(1.0)>'
