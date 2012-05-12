from __future__ import with_statement
import mock
import statsd

with mock.patch('statsd.Client') as mock_client:
    instance = mock_client.return_value
    instance._send.return_value = 1

    counter = statsd.Counter('testing')
    counter.increment('')
    mock_client._send.assert_called_with(mock.ANY, {'testing': '1|c'})

    counter.increment('', 2)
    mock_client._send.assert_called_with(mock.ANY, {'testing': '2|c'})

    counter.decrement('')
    mock_client._send.assert_called_with(mock.ANY, {'testing': '-1|c'})

    counter.decrement('', 2)
    mock_client._send.assert_called_with(mock.ANY, {'testing': '-2|c'})

