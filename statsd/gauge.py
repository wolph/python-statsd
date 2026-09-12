"""Gauges.

A gauge reports the current level of something, such as a queue depth or
a temperature, and the statsd server remembers the last value it saw.
Relative updates are sent with the statsd ``+``/``-`` prefix through
:meth:`Gauge.increment` and :meth:`Gauge.decrement`.
"""

import decimal

from statsd.client import Client

_NUM_TYPES = (int, float, decimal.Decimal)


class Gauge(Client):
    """Class to implement a statsd gauge"""

    def _send_value(self, subname: str | None, value: object) -> bool:
        """Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended
            to the client name)
        :type subname: str
        :keyword value: The gauge value to send
        """
        name = self._get_name(self.name, subname)
        self.logger.info('%s: %s', name, value)
        return self._send({name: f'{value}|g'})

    def send(
        self,
        subname: str | None,
        value: int | float | decimal.Decimal,
    ) -> bool:
        """Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended
            to the client name)
        :type subname: str
        :keyword value: The gauge value to send
        """
        if not isinstance(value, _NUM_TYPES):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f'gauge values must be numeric, got {value!r}')
        return self._send_value(subname, value)

    def increment(
        self,
        subname: str | None = None,
        delta: float = 1,
    ) -> bool:
        """Increment the gauge with `delta`

        :keyword subname: The subname to report the data to (appended
            to the client name)
        :type subname: str
        :keyword delta: The delta to add to the gauge
        :type delta: int

        >>> gauge = Gauge('application_name')
        >>> gauge.increment('gauge_name', 10)
        True
        >>> gauge.increment(delta=10)
        True
        >>> gauge.increment('gauge_name')
        True
        """
        return self._send_value(subname, f'{int(delta):+d}')

    def decrement(
        self,
        subname: str | None = None,
        delta: float = 1,
    ) -> bool:
        """Decrement the gauge with `delta`

        :keyword subname: The subname to report the data to (appended
            to the client name)
        :type subname: str
        :keyword delta: The delta to remove from the gauge
        :type delta: int

        >>> gauge = Gauge('application_name')
        >>> gauge.decrement('gauge_name', 10)
        True
        >>> gauge.decrement(delta=10)
        True
        >>> gauge.decrement('gauge_name')
        True
        """
        return self._send_value(subname, f'{-int(delta):+d}')

    def __add__(self, delta: float) -> 'Gauge':
        """Increment the gauge with `delta`

        :keyword delta: The delta to add to the gauge
        :type delta: int
        """
        self.increment(delta=delta)
        return self

    def __sub__(self, delta: float) -> 'Gauge':
        """Decrement the gauge with `delta`

        :keyword delta: The delta to remove from the gauge
        :type delta: int
        """
        self.decrement(delta=delta)
        return self

    def set(
        self,
        subname: str | None,
        value: int | float | decimal.Decimal,
    ) -> bool:
        """Set the gauge to `value`

        Gauges work like this (from the statsd docs,
        https://github.com/etsy/statsd/blob/master/docs/metric_types.md):

            Adding a sign to the gauge value will change the value,
            rather than setting it.

                gaugor:-10|g
                gaugor:+4|g

            So if gaugor was 333, those commands would set it to
            333 - 10 + 4, or 327.

            Note: This implies you can't explicitly set a gauge to a
            negative number without first setting it to zero.

        :keyword subname: The subname to report the data to (appended
            to the client name)
        :type subname: str
        :keyword value: The new gauge value
        """
        if not isinstance(value, _NUM_TYPES):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f'gauge values must be numeric, got {value!r}')
        if value < 0:
            self._send_value(subname, 0)
        return self._send_value(subname, value)
