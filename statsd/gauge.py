import statsd

from . import compat


class Gauge(statsd.Client):
    '''Class to implement a statsd gauge

    '''

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
