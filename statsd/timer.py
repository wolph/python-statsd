"""Timers.

A timer measures how long something took and lets the statsd server
compute the percentiles. The measurement is taken with
:func:`time.perf_counter`, so a clock adjustment cannot turn a duration
negative, and the same timer can be driven by explicit
:meth:`Timer.start` and :meth:`Timer.stop` calls, as a context manager,
or as a decorator.
"""

import contextlib
import functools
import time
from collections.abc import Callable, Generator
from types import TracebackType
from typing import ParamSpec, TypeVar, overload

from statsd.client import Client
from statsd.connection import Connection

_P = ParamSpec('_P')
_R = TypeVar('_R')


class Timer(Client):
    """Statsd Timer Object

    Additional documentation is available at the parent class
    :class:`~statsd.client.Client`

    :keyword name: The name for this timer
    :type name: str
    :keyword connection: The connection to use, will be automatically
        created if not given
    :type connection: :class:`~statsd.connection.Connection`
    :keyword min_send_threshold: Timings smaller than this will not be
        sent, use -1 to send everything
    :type min_send_threshold: float

    >>> timer = Timer('application_name').start()
    >>> # do something
    >>> timer.stop('executed_action')
    True
    """

    def __init__(
        self,
        name: str | bytes,
        connection: Connection | None = None,
        min_send_threshold: float = -1,
    ) -> None:
        super().__init__(name, connection=connection)
        self._start: float | None = None
        self._last: float | None = None
        self._stop: float | None = None
        self.min_send_threshold: float = min_send_threshold

    def start(self) -> 'Timer':
        """Start the timer and store the start time, this can only be
        executed once per instance.

        The timer instance is returned so it can be chained when
        instantiating the timer instance like this:
        ``timer = Timer('application_name').start()``
        """
        if self._start is not None:
            raise RuntimeError('Unable to start, the timer is already running')
        self._last = self._start = time.perf_counter()
        return self

    def send(self, subname: str, delta: float) -> bool:
        """Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended
            to the client name)
        :type subname: str
        :keyword delta: The time delta (in seconds) to report
        :type delta: float
        """
        ms = delta * 1000
        if ms <= self.min_send_threshold:
            return True
        name = self._get_name(self.name, subname)
        self.logger.info('%s: %0.08fms', name, ms)
        return self._send({name: f'{ms:0.08f}|ms'})

    def intermediate(self, subname: str) -> bool:
        """Send the time that has passed since our last measurement

        :keyword subname: The subname to report the data to (appended
            to the client name)
        :type subname: str
        """
        if self._last is None:
            raise RuntimeError(
                'Unable to send intermediate time, the timer was never started'
            )
        current_time = time.perf_counter()
        response = self.send(subname, current_time - self._last)
        self._last = current_time
        return response

    def stop(self, subname: str = 'total') -> bool:
        """Stop the timer and send the total since `start()` was run

        :keyword subname: The subname to report the data to (appended
            to the client name)
        :type subname: str
        """
        if self._start is None:
            raise RuntimeError('Unable to stop, the timer was never started')
        if self._stop is not None:
            raise RuntimeError('Unable to stop, the timer is already stopped')
        self._stop = time.perf_counter()
        return self.send(subname, self._stop - self._start)

    def __enter__(self) -> 'Timer':
        return self.start()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Stop the timer and send the total, also when the block
        raised an exception."""
        self.stop()

    def _decorate(
        self,
        name: str,
        function: Callable[_P, _R],
        class_: type['Timer'] | None = None,
    ) -> Callable[_P, _R]:
        if class_ is None:
            class_ = Timer

        @functools.wraps(function)
        def _decorator(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            timer = self.get_client(name, class_)
            timer.start()
            try:
                return function(*args, **kwargs)
            finally:
                # Stop the timer and send the total, also on exceptions
                timer.stop('')

        return _decorator

    @overload
    def decorate(
        self,
        function_or_name: Callable[_P, _R],
    ) -> Callable[_P, _R]: ...

    @overload
    def decorate(
        self,
        function_or_name: str,
    ) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]: ...

    def decorate(
        self,
        function_or_name: 'Callable[_P, _R] | str',
    ) -> 'Callable[_P, _R] | Callable[[Callable[_P, _R]], Callable[_P, _R]]':
        """Decorate a function to time the execution

        The wrapped function will be timed without needing a name, if
        no name is given the function defaults to the name of the
        function.

        :keyword function_or_name: The name to post to or the function
            to wrap

        >>> from statsd import Timer
        >>> timer = Timer('application_name')
        >>>
        >>> @timer.decorate
        ... def some_function():
        ...     # resulting timer name: application_name.some_function
        ...     pass
        >>>
        >>> @timer.decorate('my_timer')
        ... def some_other_function():
        ...     # resulting timer name: application_name.my_timer
        ...     pass
        """
        if isinstance(function_or_name, str):
            return functools.partial(self._decorate, function_or_name)
        name: str = getattr(
            function_or_name, '__name__', type(function_or_name).__name__
        )
        return self._decorate(name, function_or_name)

    @contextlib.contextmanager
    def time(
        self,
        subname: str | None = None,
        class_: type['Timer'] | None = None,
    ) -> Generator['Timer', None, None]:
        """Context manager to time the execution of a block of code

        The timed metric is also sent when the block raises an
        exception.

        :keyword subname: The subname to report the data to (appended
            to the client name)
        :type subname: str
        :keyword class_: The :class:`Timer` subclass to use
        :type class_: :class:`Timer`

        >>> from statsd import Timer
        >>> timer = Timer('application_name')
        >>>
        >>> with timer.time():
        ...     # resulting timer name: application_name
        ...     pass
        >>>
        >>> with timer.time('context_timer'):
        ...     # resulting timer name: application_name.context_timer
        ...     pass
        """
        if class_ is None:
            class_ = Timer
        timer = self.get_client(subname, class_)
        timer.start()
        try:
            yield timer
        finally:
            timer.stop('')
