from __future__ import with_statement
from unittest import TestCase
import mock
import statsd


class TestCounter(TestCase):

    def setUp(self):
        self.counter = statsd.Counter('testing')

    def test_increment(self):
        with mock.patch('statsd.Client') as mock_client:
            self.counter.increment('')
            mock_client._send.assert_called_with(mock.ANY, {'testing': '1|c'})

    def test_increment_with_an_int(self):
        with mock.patch('statsd.Client') as mock_client:
            self.counter.increment('', 2)
            mock_client._send.assert_called_with(mock.ANY, {'testing': '2|c'})

    def test_decrement(self):
        with mock.patch('statsd.Client') as mock_client:
            self.counter.decrement('')
            mock_client._send.assert_called_with(mock.ANY, {'testing': '-1|c'})

    def test_decrement_with_an_int(self):
        with mock.patch('statsd.Client') as mock_client:
            self.counter.decrement('', 2)
            mock_client._send.assert_called_with(mock.ANY, {'testing': '-2|c'})
