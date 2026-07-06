from unittest import mock

import statsd


def test_send(udp_socket: mock.MagicMock) -> None:
    average = statsd.Average('testing')
    assert average.send('spam', 123) is True
    udp_socket.send.assert_called_once_with(b'testing.spam:123|a')


def test_send_float_truncates(udp_socket: mock.MagicMock) -> None:
    average = statsd.Average('testing')
    assert average.send('spam', 123.9) is True
    udp_socket.send.assert_called_once_with(b'testing.spam:123|a')
