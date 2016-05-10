import statsd

from . import compat


class Gauge(statsd.Client):

    'Class to implement a statsd gauge'

    def _send(self, subname, value):
        '''Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :type subname: str
        :keyword value: The gauge value to send
        '''
        name = self._get_name(self.name, subname)
        self.logger.info('%s: %s', name, value)
        return statsd.Client._send(self, {name: '%s|g' % value})

    def send(self, subname, value):
        '''Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :type subname: str
        :keyword value: The gauge value to send
        '''
        assert isinstance(value, compat.NUM_TYPES)
        return self._send(subname, value)

    def increment(self, subname=None, delta=1):
        '''Increment the gauge with `delta`

        :keyword subname: The subname to report the data to (appended to the
            client name)
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
        '''
        delta = int(delta)
        sign = "+" if delta >= 0 else ""
        return self._send(subname, "%s%d" % (sign, delta))

    def decrement(self, subname=None, delta=1):
        '''Decrement the gauge with `delta`

        :keyword subname: The subname to report the data to (appended to the
            client name)
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
        '''
        delta = -int(delta)
        sign = "+" if delta >= 0 else ""
        return self._send(subname, "%s%d" % (sign, delta))

    def __add__(self, delta):
        '''Increment the gauge with `delta`

        :keyword delta: The delta to add to the gauge
        :type delta: int

        >>> gauge = Gauge('application_name')
        >>> gauge += 5
        '''
        self.increment(delta=delta)
        return self

    def __sub__(self, delta):
        '''Decrement the gauge with `delta`

        :keyword delta: The delta to remove from the gauge
        :type delta: int

        >>> gauge = Gauge('application_name')
        >>> gauge -= 5
        '''
        self.decrement(delta=delta)
        return self

    def set(self, subname, value):
        '''
        Set the data ignoring the sign, ie set("test", -1) will set "test"
        exactly to -1 (not decrement it by 1)

        See https://github.com/etsy/statsd/blob/master/docs/metric_types.md
        "Adding a sign to the gauge value will change the value, rather
        than setting it.

            gaugor:-10|g
            gaugor:+4|g

        So if gaugor was 333, those commands would set it to 333 - 10 + 4, or
        327.

        Note: This implies you can't explicitly set a gauge to a negative
        number without first setting it to zero."

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :type subname: str
        :keyword value: The new gauge value
        '''

        assert isinstance(value, compat.NUM_TYPES)
        if value < 0:
            self._send(subname, 0)
        return self._send(subname, value)
