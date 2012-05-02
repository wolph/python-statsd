import statsd


class Raw(statsd.Client):
    '''Class to implement a statsd raw message.
    If a service has already summarized its own
    data for e.g. inspection purposes, use this
    summarized data to send to a statsd that has
    the raw patch, and this data will be sent
    to graphite pretty much unchanged.

    See https://github.com/chuyskywalker/statsd/blob/master/README.md for more info.
    '''

    def send(self, subname, value):
        '''Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :keyword value: The raw value to send
        '''
        name = self._get_name(self.name, subname)
        self.logger.info('%s: %d'% (name, value))
        return statsd.Client._send(self, {name: '%d|r' % value})
