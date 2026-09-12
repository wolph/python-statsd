"""Counters.

A counter reports a delta rather than a level, and the statsd server
adds those deltas up over the flush interval. Increments can be written
as method calls or with the ``+=`` and ``-=`` operators, whichever reads
better at the call site.
"""

from statsd.client import Client


class Counter(Client):
    """Class to implement a statsd counter

    Additional documentation is available at the parent class
    :class:`~statsd.client.Client`

    The values can be incremented/decremented by using either the
    `increment()` and `decrement()` methods or by simply adding/deleting
    from the object.

    >>> counter = Counter('application_name')
    >>> counter += 10

    >>> counter = Counter('application_name')
    >>> counter -= 10
    """

    def _send_delta(self, subname: str | None, delta: int) -> bool:
        """Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended
            to the client name)
        :type subname: str
        :keyword delta: The delta to add to/remove from the counter
        :type delta: int
        """
        name = self._get_name(self.name, subname)
        self.logger.info('%s: %d', name, delta)
        return self._send({name: f'{delta}|c'})

    def increment(
        self,
        subname: str | None = None,
        delta: float = 1,
    ) -> bool:
        """Increment the counter with `delta`

        :keyword subname: The subname to report the data to (appended
            to the client name)
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
        """
        return self._send_delta(subname, int(delta))

    def decrement(
        self,
        subname: str | None = None,
        delta: float = 1,
    ) -> bool:
        """Decrement the counter with `delta`

        :keyword subname: The subname to report the data to (appended
            to the client name)
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
        """
        return self._send_delta(subname, -int(delta))

    def __add__(self, delta: float) -> 'Counter':
        """Increment the counter with `delta`

        :keyword delta: The delta to add to the counter
        :type delta: int
        """
        self.increment(delta=delta)
        return self

    def __sub__(self, delta: float) -> 'Counter':
        """Decrement the counter with `delta`

        :keyword delta: The delta to remove from the counter
        :type delta: int
        """
        self.decrement(delta=delta)
        return self


def increment(key: str, delta: float = 1) -> bool:
    """Increment the counter with `delta`

    :keyword key: The key to report the data to
    :type key: str
    :keyword delta: The delta to add to the counter
    :type delta: int
    """
    return Counter(key).increment(delta=delta)


def decrement(key: str, delta: float = 1) -> bool:
    """Decrement the counter with `delta`

    :keyword key: The key to report the data to
    :type key: str
    :keyword delta: The delta to remove from the counter
    :type delta: int
    """
    return Counter(key).decrement(delta=delta)
