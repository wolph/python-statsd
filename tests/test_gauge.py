from __future__ import with_statement
from unittest import TestCase
from decimal import Decimal
import mock
import statsd


class TestGauge(TestCase):

    def setUp(self):
        self.gauge = statsd.Gauge('testing')

    def test_send_float(self):
        with mock.patch('statsd.Client') as mock_client:
            self.gauge.send('', 10.5)
            mock_client._send.assert_called_with(mock.ANY,
                                                 {'testing': '10.5|g'})

    def test_send_decimal(self):
        with mock.patch('statsd.Client') as mock_client:
            self.gauge.send('', Decimal('6.576'))
            mock_client._send.assert_called_with(mock.ANY,
                                                 {'testing': '6.576|g'})

    def test_send_integer(self):
        with mock.patch('statsd.Client') as mock_client:
            self.gauge.send('', 1)
            mock_client._send.assert_called_with(mock.ANY,
                                                 {'testing': '1|g'})

    def test_set(self):
        with mock.patch('statsd.Client') as mock_client:
            self.gauge.set('', -1)
            mock_client._send.assert_any_call(mock.ANY, {'testing': '0|g'})
            mock_client._send.assert_any_call(mock.ANY, {'testing': '-1|g'})
            mock_client.reset_mock()
            self.gauge.set('', 1)
            mock_client._send.assert_called_with(mock.ANY, {'testing': '1|g'})
