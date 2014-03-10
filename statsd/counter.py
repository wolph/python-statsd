import statsd


class Counter(statsd.Client):
    '''Class to implement a statd counter

    Additional documentation is available at the
    parent class :class:`~statsd.client.Client`

    The values can be incremented/decremented by using either the
    `increment()` and `decrement()` methods or by simply adding/deleting from
    the object.

    >>> counter = Counter('application_name')
    >>> counter += 10

    >>> counter = Counter('application_name')
    >>> counter -= 10
    '''

    def _send(self, subname, delta):
        '''Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :type subname: str
        :keyword delta: The delta to add to/remove from the counter
        :type delta: int
        '''
        name = self._get_name(self.name, subname)
        self.logger.info('%s: %d', name, delta)
        return statsd.Client._send(self, {name: '%d|c' % delta})

    def increment(self, subname=None, delta=1):
        '''Increment the counter with `delta`

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :type subname: str
        :keyword delta: The delta to add to the counter
        :type delta: int

        >>> counter = Counter('application_name')
        >>> counter.increment('counter_name', 10)
        True
        >>> counter.increment(delta=10)
        True
        >>> counter.increment('counter_name')
        True
        '''
        return self._send(subname, int(delta))

    def decrement(self, subname=None, delta=1):
        '''Decrement the counter with `delta`

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :type subname: str
        :keyword delta: The delta to remove from the counter
        :type delta: int

        >>> counter = Counter('application_name')
        >>> counter.decrement('counter_name', 10)
        True
        >>> counter.decrement(delta=10)
        True
        >>> counter.decrement('counter_name')
        True
        '''
        return self._send(subname, -int(delta))

    def __add__(self, delta):
        '''Increment the counter with `delta`

        :keyword delta: The delta to add to the counter
        :type delta: int
        '''
        self.increment(delta=delta)
        return self

    def __sub__(self, delta):
        '''Decrement the counter with `delta`

        :keyword delta: The delta to remove from the counter
        :type delta: int
        '''
        self.decrement(delta=delta)
        return self


def increment(key, delta=1):
    '''Increment the counter with `delta`

    :keyword key: The key to report the data to
    :type key: str
    :keyword delta: The delta to add to the counter
    :type delta: int
    '''
    return Counter(key).increment(delta=delta)


def decrement(key, delta=1):
    '''Decrement the counter with `delta`

    :keyword key: The key to report the data to
    :type key: str
    :keyword delta: The delta to remove from the counter
    :type delta: int
    '''
    return Counter(key).decrement(delta=delta)

