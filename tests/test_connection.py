import mock
import statsd
import unittest


class ConnectionException(Exception):

    pass


class TestConnection(unittest.TestCase):

    def test_set_disabled_to_false_by_default(self):
        result = statsd.connection.Connection()
        assert result._disabled is False

    def test_send_returns_false_if_disabled(self):
        connection = statsd.connection.Connection(disabled=True)
        assert connection.send({'data': True}) is False
        assert connection.send({'data': True}, 1) is False

    @mock.patch('socket.socket')
    def test_send_returns_true_if_enabled(self, mock_class):
        connection = statsd.connection.Connection()
        assert connection.send({'data': True}) is True
        assert connection.send({'test:1|c': True}, 0.99999999)
        assert connection.send({'test:1|c': True}, 0.00000001)
        assert connection.send({'data': True}, 1) is True

    def test_send_exception(self, mock_class=None):
        connection = statsd.connection.Connection()
        socket = mock.MagicMock()
        send = mock.PropertyMock(side_effect=ConnectionException)
        type(socket).send = send
        connection.udp_sock = socket
        assert not connection.send({'data': True})

    def test_connection_set_defaults(self):
        connection = statsd.connection.Connection()
        assert connection._host == 'localhost'
        assert connection._port == 8125
        assert connection._sample_rate == 1
        assert connection._disabled is False

        statsd.connection.Connection.set_defaults('127.0.0.1', 1234, 10, True)
        connection = statsd.connection.Connection()
        assert connection._host == '127.0.0.1'
        assert connection._port == 1234
        assert connection._sample_rate == 10
        assert connection._disabled is True

        statsd.connection.Connection.set_defaults()
        connection = statsd.connection.Connection()
        assert connection._host == 'localhost'
        assert connection._port == 8125
        assert connection._sample_rate == 1
        assert connection._disabled is False

    def test_repr(self):
        connection = statsd.connection.Connection()
        assert '<Connection[localhost:8125] P(1.0)>' == repr(connection)


