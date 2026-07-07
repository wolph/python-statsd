from collections.abc import Iterator
from unittest import mock

import pytest
import statsd


@pytest.fixture
def perf_counter() -> Iterator[mock.MagicMock]:
    """Fake time.perf_counter ticking 0.1234s per call."""

    def generator() -> Iterator[float]:
        i = 0.0
        while True:
            i += 0.1234
            yield i

    with mock.patch('time.perf_counter', side_effect=generator()) as m:
        yield m


def get_time(udp_socket: mock.MagicMock, key: str) -> float:
    data = udp_socket.send.call_args[0][0].decode()
    name, _, value = data.partition(':')
    assert name == key
    assert value.endswith('|ms')
    return round(float(value.removesuffix('|ms')), 4)


@pytest.mark.usefixtures('perf_counter')
class TestDecorator:
    def test_bare(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('timer')

        @timer.decorate
        def a() -> None:
            pass

        a()
        assert get_time(udp_socket, 'timer.a') == 123.4

    def test_named(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('timer')

        @timer.decorate('spam')
        def a() -> None:
            pass

        a()
        assert get_time(udp_socket, 'timer.spam') == 123.4
        assert a.__name__ == 'a'

    def test_nested_naming(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('timer').get_client('eggs0')

        @timer.decorate('d0')
        def a() -> None:
            pass

        a()
        assert get_time(udp_socket, 'timer.eggs0.d0') == 123.4

    def test_sends_on_exception(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('timer')

        @timer.decorate
        def a() -> None:
            raise ValueError('boom')

        with pytest.raises(ValueError, match='boom'):
            a()
        assert get_time(udp_socket, 'timer.a') == 123.4

    def test_return_value(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('timer')

        @timer.decorate
        def a() -> int:
            return 42

        assert a() == 42

    def test_decorate_with_explicit_class(
        self, udp_socket: mock.MagicMock
    ) -> None:
        used: list[type] = []

        class CustomTimer(statsd.Timer):
            def send(self, subname: str, delta: float) -> bool:
                used.append(type(self))
                return super().send(subname, delta)

        timer = statsd.Timer('timer')

        def a() -> None:
            pass

        decorated = timer._decorate('custom', a, class_=CustomTimer)
        decorated()
        assert used == [CustomTimer]
        assert get_time(udp_socket, 'timer.custom') == 123.4


@pytest.mark.usefixtures('perf_counter')
class TestContextManager:
    def test_with_timer(self, udp_socket: mock.MagicMock) -> None:
        with statsd.Timer('cm'):
            pass
        assert get_time(udp_socket, 'cm.total') == 123.4

    def test_time_default(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('cm').get_client('default')
        with timer.time():
            pass
        assert get_time(udp_socket, 'cm.default') == 123.4

    def test_time_named(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('cm').get_client('named')
        with timer.time('name'):
            pass
        assert get_time(udp_socket, 'cm.named.name') == 123.4

    def test_time_class(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('cm').get_client('named')
        with timer.time(class_=statsd.Timer):
            pass
        assert get_time(udp_socket, 'cm.named') == 123.4

    def test_time_yields_timer(self) -> None:
        timer = statsd.Timer('cm')
        with timer.time('sub') as inner:
            assert isinstance(inner, statsd.Timer)
            assert inner.name == 'cm.sub'

    def test_time_sends_on_exception(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('cm')
        with pytest.raises(ValueError, match='boom'):
            with timer.time('failing'):
                raise ValueError('boom')
        assert get_time(udp_socket, 'cm.failing') == 123.4


@pytest.mark.usefixtures('perf_counter')
class TestStartStop:
    def test_stop_default_subname(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('timer4')
        timer.start()
        assert timer.stop() is True
        assert get_time(udp_socket, 'timer4.total') == 123.4

    def test_stop_named_subname(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('timer5')
        timer.start()
        assert timer.stop('test') is True
        assert get_time(udp_socket, 'timer5.test') == 123.4

    def test_chained_start(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('timer').start()
        assert isinstance(timer, statsd.Timer)
        assert timer.stop() is True

    def test_intermediate(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('timer6')
        timer.start()
        timer.intermediate('extras')
        assert get_time(udp_socket, 'timer6.extras') == 123.4
        timer.stop()
        assert get_time(udp_socket, 'timer6.total') == 246.8

    def test_intermediate_named_stop(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('timer7')
        timer.start()
        timer.intermediate('extras')
        assert get_time(udp_socket, 'timer7.extras') == 123.4
        timer.stop('test')
        assert get_time(udp_socket, 'timer7.test') == 246.8


class TestStateErrors:
    def test_start_twice(self) -> None:
        timer = statsd.Timer('timer').start()
        with pytest.raises(RuntimeError, match='already running'):
            timer.start()

    def test_stop_without_start(self) -> None:
        with pytest.raises(RuntimeError, match='never started'):
            statsd.Timer('timer').stop()

    def test_stop_twice(self) -> None:
        timer = statsd.Timer('timer').start()
        timer.stop()
        with pytest.raises(RuntimeError, match='already stopped'):
            timer.stop()

    def test_intermediate_without_start(self) -> None:
        with pytest.raises(RuntimeError, match='never started'):
            statsd.Timer('timer').intermediate('spam')


class TestMinSendThreshold:
    def test_zero_timing_not_sent(self, udp_socket: mock.MagicMock) -> None:
        with mock.patch('time.perf_counter', return_value=42.0):
            timer = statsd.Timer('timer8', min_send_threshold=0)
            timer.start()
            assert timer.stop() is True
        assert not udp_socket.send.called

    def test_above_threshold_sent(self, udp_socket: mock.MagicMock) -> None:
        timer = statsd.Timer('timer9', min_send_threshold=0)
        assert timer.send('spam', 0.5) is True
        assert udp_socket.send.called
