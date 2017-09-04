from __future__ import with_statement
from unittest import TestCase
import mock
import statsd


class TestTimerBase(TestCase):

    def tearDown(self):
        self._time_patch.stop()

    def get_time(self, mock_client, key):
        return float(self.get_arg(mock_client, key).split('|')[0])

    def get_arg(self, mock_client, key):
        return mock_client._send.call_args[0][1][key]


class TestTimerDecorator(TestTimerBase):

    def setUp(self):
        self.timer = statsd.Timer('timer')

        # get time.time() to always return the same value so that this test
        # isn't system load dependant.
        self._time_patch = mock.patch('time.time')
        time_time = self._time_patch.start()

        def generator():
            i = 0.0
            while True:
                i += 0.1234
                yield i
        time_time.side_effect = generator()

    @mock.patch('statsd.Client')
    def test_decorator_a(self, mock_client):
        @self.timer.decorate
        def a():
            pass

        a()

        assert self.get_time(mock_client, 'timer.a') == 123.4, \
            'This test must execute within 2ms'

    @mock.patch('statsd.Client')
    def test_decorator_named_spam(self, mock_client):
        @self.timer.decorate('spam')
        def a():
            pass
        a()

        assert self.get_time(mock_client, 'timer.spam') == 123.4, \
            'This test must execute within 2ms'
        assert a.__name__ == 'a'

    @mock.patch('statsd.Client')
    def test_nested_naming_decorator(self, mock_client):
        timer = self.timer.get_client('eggs0')

        @timer.decorate('d0')
        def a():
            pass
        a()

        assert self.get_time(mock_client, 'timer.eggs0.d0') == 123.4, \
            'This test must execute within 2ms'


class TestTimerContextManager(TestTimerBase):

    def setUp(self):
        self.timer = statsd.Timer('cm')

        # get time.time() to always return the same value so that this test
        # isn't system load dependant.
        self._time_patch = mock.patch('time.time')
        time_time = self._time_patch.start()

        def generator():
            i = 0.0
            while True:
                i += 0.1234
                yield i
        time_time.side_effect = generator()

    @mock.patch('statsd.Client')
    def test_context_manager_default(self, mock_client):
        timer = self.timer.get_client('default')
        with timer.time():
            pass

        assert self.get_time(mock_client, 'cm.default') == 123.4, \
            'This test must execute within 2ms'

    @mock.patch('statsd.Client')
    def test_context_manager_named(self, mock_client):
        timer = self.timer.get_client('named')
        with timer.time('name'):
            pass

        assert self.get_time(mock_client, 'cm.named.name') == 123.4, \
            'This test must execute within 2ms'

    @mock.patch('statsd.Client')
    def test_context_manager_class(self, mock_client):
        timer = self.timer.get_client('named')
        with timer.time(class_=statsd.Timer):
            pass

        assert self.get_time(mock_client, 'cm.named') == 123.4, \
            'This test must execute within 2ms'


class TestTimerAdvancedUsage(TestTimerDecorator):

    @mock.patch('statsd.Client')
    def test_timer_total(self, mock_client):
        timer4 = statsd.Timer('timer4')
        timer4.start()
        timer4.stop()
        assert self.get_time(mock_client, 'timer4.total') == 123.4, \
            'This test must execute within 2ms'

        timer5 = statsd.Timer('timer5')
        timer5.start()
        timer5.stop('test')
        assert self.get_time(mock_client, 'timer5.test') == 123.4, \
            'This test must execute within 2ms'

    @mock.patch('statsd.Client')
    def test_timer_intermediate(self, mock_client):
        timer6 = statsd.Timer('timer6')
        timer6.start()
        timer6.intermediate('extras')
        assert self.get_time(mock_client, 'timer6.extras') == 123.4, \
            'This test must execute within 2ms'
        timer6.stop()
        assert self.get_time(mock_client, 'timer6.total') == 370.2, \
            'This test must execute within 2ms'

        timer7 = statsd.Timer('timer7')
        timer7.start()
        timer7.intermediate('extras')
        assert self.get_time(mock_client, 'timer7.extras') == 123.4, \
            'This test must execute within 2ms'
        timer7.stop('test')
        assert self.get_time(mock_client, 'timer7.test') == 370.2, \
            'This test must execute within 2ms'


class TestTimerZero(TestTimerBase):

    def setUp(self):
        # get time.time() to always return the same value so that this test
        # isn't system load dependant.
        self._time_patch = mock.patch('time.time')
        time_time = self._time_patch.start()

        def generator():
            while True:
                yield 0
        time_time.side_effect = generator()

    def tearDown(self):
        self._time_patch.stop()

    @mock.patch('statsd.Client')
    def test_timer_zero(self, mock_client):
        timer8 = statsd.Timer('timer8', min_send_threshold=0)
        timer8.start()
        timer8.stop()
        assert mock_client._send.call_args is None, \
            '0 timings shouldnt be sent'

        timer9 = statsd.Timer('timer9', min_send_threshold=0)
        timer9.start()
        timer9.stop('test')
        assert mock_client._send.call_args is None, \
            '0 timings shouldnt be sent'

