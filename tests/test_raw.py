from unittest import mock

import statsd


def test_send_with_timestamp(udp_socket: mock.MagicMock) -> None:
    raw = statsd.Raw('testing')
    assert raw.send('spam', 12435, 1234567890) is True
    udp_socket.send.assert_called_once_with(b'testing.spam:12435|r|1234567890')


def test_send_default_timestamp(udp_socket: mock.MagicMock) -> None:
    raw = statsd.Raw('testing')
    with mock.patch('time.time', return_value=1234567890.5):
        assert raw.send('spam', 12435) is True
    udp_socket.send.assert_called_once_with(b'testing.spam:12435|r|1234567890')
