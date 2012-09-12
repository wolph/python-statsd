from unittest import TestCase
from statsd.connection import Connection


class TestConnection(TestCase):

    def test_set_disabled_to_false_by_default(self):
        result = Connection()
        assert result._disabled is False

    def test_send_returns_false_if_disabled(self):
        conn = Connection(disabled=True)
        assert conn.send({'data':True}, 1) is False

    def test_send_returns_true_if_enabled(self):
        conn = Connection()
        result = conn.send({'data':True}, 1)
        assert result is True

