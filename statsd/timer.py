import contextlib
import time
from functools import wraps, partial

import statsd


class Timer(statsd.Client):

    '''
    Statsd Timer Object

    Additional documentation is available at the parent class
    :class:`~statsd.client.Client`

    :keyword name: The name for this timer
    :type name: str
    :keyword connection: The connection to use, will be automatically created
        if not given
    :type connection: :class:`~statsd.connection.Connection`
    :keyword min_send_threshold: Timings smaller than this will not be sent so
        -1 can be used for all.
    :type min_send_threshold: int

    >>> timer = Timer('application_name').start()
    >>>  # do something
    >>> timer.stop('executed_action')
    True
    '''

    def __init__(self, name, connection=None, min_send_threshold=-1):
        super(Timer, self).__init__(name, connection=connection)
        self._start = None
        self._last = None
        self._stop = None
        self.min_send_threshold = min_send_threshold

    def start(self):
        '''Start the timer and store the start time, this can only be executed
        once per instance

        It returns the timer instance so it can be chained when instantiating
        the timer instance like this:
        ``timer = Timer('application_name').start()``'''
        assert self._start is None, (
            'Unable to start, the timer is already running')
        self._last = self._start = time.time()
        return self

    def send(self, subname, delta):
        '''Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :type subname: str
        :keyword delta: The time delta (time.time() - time.time()) to report
        :type delta: float
        '''
        ms = delta * 1000
        if ms > self.min_send_threshold:
            name = self._get_name(self.name, subname)
            self.logger.info('%s: %0.08fms', name, ms)
            return statsd.Client._send(self, {name: '%0.08f|ms' % ms})
        else:
            return True

    def intermediate(self, subname):
        '''Send the time that has passed since our last measurement

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :type subname: str
        '''
        t = time.time()
        response = self.send(subname, t - self._last)
        self._last = t
        return response

    def stop(self, subname='total'):
        '''Stop the timer and send the total since `start()` was run

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :type subname: str
        '''
        assert self._stop is None, (
            'Unable to stop, the timer is already stopped')
        self._stop = time.time()
        return self.send(subname, self._stop - self._start)

    def _decorate(self, name, function, class_=None):
        class_ = class_ or Timer

        @wraps(function)
        def _decorator(*args, **kwargs):
            timer = self.get_client(name, class_)
            timer.start()
            try:
                return function(*args, **kwargs)
            finally:
                # Stop the timer, send the message and cleanup
                timer.stop('')

        return _decorator

    def decorate(self, function_or_name):
        '''Decorate a function to time the execution

        The method can be called with or without a name. If no name is given
        the function defaults to the name of the function.

        :keyword function_or_name: The name to post to or the function to wrap

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

        '''
        if callable(function_or_name):
            return self._decorate(function_or_name.__name__, function_or_name)
        else:
            return partial(self._decorate, function_or_name)

    @contextlib.contextmanager
    def time(self, subname=None, class_=None):
        '''Returns a context manager to time execution of a block of code.

        :keyword subname: The subname to report data to
        :type subname: str
        :keyword class_: The :class:`~statsd.client.Client` subclass to use
            (e.g. :class:`~statsd.timer.Timer` or
            :class:`~statsd.counter.Counter`)
        :type class_: :class:`~statsd.client.Client`

        >>> from statsd import Timer
        >>> timer = Timer('application_name')
        >>>
        >>> with timer.time():
        ...     # resulting timer name: application_name
        ...     pass
        >>>
        >>>
        >>> with timer.time('context_timer'):
        ...     # resulting timer name: application_name.context_timer
        ...     pass

        '''
        if class_ is None:
            class_ = Timer
        timer = self.get_client(subname, class_)
        timer.start()
        yield
        timer.stop('')
