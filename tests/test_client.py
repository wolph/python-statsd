import statsd
from unittest import TestCase


class TestClient(TestCase):

    def test_average_shortcut(self):
        average = statsd.Client('average').get_average()
        assert isinstance(average, statsd.Average)

    def test_counter_shortcut(self):
        counter = statsd.Client('counter').get_counter()
        assert isinstance(counter, statsd.Counter)

    def test_gauge_shortcut(self):
        gauge = statsd.Client('gauge').get_gauge()
        assert isinstance(gauge, statsd.Gauge)

    def test_raw_shortcut(self):
        raw = statsd.Client('raw').get_raw()
        assert isinstance(raw, statsd.Raw)

    def test_timer_shortcut(self):
        timer = statsd.Client('timer').get_timer()
        assert isinstance(timer, statsd.Timer)
