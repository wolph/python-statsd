from decimal import Decimal
import mock
import statsd

with mock.patch('statsd.Client') as mock_client:
    instance = mock_client.return_value
    instance._send.return_value = 1

    gauge = statsd.Gauge('testing')
    gauge.send('', 10.5)
    mock_client._send.assert_called_with(mock.ANY, {'testing': '10.5|g'})

    gauge.send('', Decimal('6.576'))
    mock_client._send.assert_called_with(mock.ANY, {'testing': '6.576|g'})

    gauge.send('', 1)
    mock_client._send.assert_called_with(mock.ANY, {'testing': '1|g'})

