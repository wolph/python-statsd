import statsd
import datetime as dt


class Raw(statsd.Client):
    '''Class to implement a statsd raw message.
    If a service has already summarized its own
    data for e.g. inspection purposes, use this
    summarized data to send to a statsd that has
    the raw patch, and this data will be sent
    to graphite pretty much unchanged.

    See https://github.com/chuyskywalker/statsd/blob/master/README.md for
    more info.

    >>> raw = Raw('test')
    >>> raw.send('name', 12435)
    True
    >>> import time
    >>> raw.send('name', 12435, time.time())
    True
    '''

    def send(self, subname, value, timestamp=None):
        '''Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :type subname: str
        :keyword value: The raw value to send
        '''
        if timestamp is None:
            ts = int(dt.datetime.now().strftime("%s"))
        else:
            ts = timestamp
        name = self._get_name(self.name, subname)
        self.logger.info('%s: %s %s' % (name, value, ts))
        return statsd.Client._send(self, {name: '%s|r|%s' % (value, ts)})

