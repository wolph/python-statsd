from __future__ import with_statement
from unittest import TestCase
import mock
import statsd


class TestTimerDecorator(TestCase):

    def setUp(self):
        self.timer = statsd.Timer('timer')

    def test_decorator_a(self):
        with mock.patch('statsd.Client') as mock_client:
            @self.timer.decorate
            def a():
                pass
            a()
        mock_client._send.assert_called_with(mock.ANY, {'timer.a': '0|ms'})

    def test_decorator_named_spam(self):
        with mock.patch('statsd.Client') as mock_client:
            @self.timer.decorate('spam')
            def a():
                pass
            a()
        mock_client._send.assert_called_with(mock.ANY, {'timer.spam': '0|ms'})

    def test_nested_naming_decorator(self):
        with mock.patch('statsd.Client') as mock_client:
            timer = self.timer.get_client('eggs0')
            @timer.decorate('d0')
            def a():
                pass
            a()
        mock_client._send.assert_called_with(mock.ANY, {'timer.eggs0.d0': '0|ms'})


class TestTimerAdvancedUsage(TestTimerDecorator):

    def test_timer_total(self):
        with mock.patch('statsd.Client') as mock_client:
            timer4 = statsd.Timer('timer4')
            timer4.start()
            timer4.stop()
            mock_client._send.assert_called_with(mock.ANY, {'timer4.total': '0|ms'})

            timer5 = statsd.Timer('timer5')
            timer5.start()
            timer5.stop('test')
            mock_client._send.assert_called_with(mock.ANY, {'timer5.test': '0|ms'})

    def test_timer_intermediate(self):
        with mock.patch('statsd.Client') as mock_client:
            timer6 = statsd.Timer('timer6')
            timer6.start()
            timer6.intermediate('extras')
            mock_client._send.assert_called_with(mock.ANY, {'timer6.extras': '0|ms'})
            timer6.stop()
            mock_client._send.assert_called_with(mock.ANY, {'timer6.total': '0|ms'})

            timer7 = statsd.Timer('timer7')
            timer7.start()
            timer7.intermediate('extras')
            mock_client._send.assert_called_with(mock.ANY, {'timer7.extras': '0|ms'})
            timer7.stop('test')
            mock_client._send.assert_called_with(mock.ANY, {'timer7.test': '0|ms'})
