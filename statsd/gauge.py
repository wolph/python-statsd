import statsd


class Gauge(statsd.Client):
    '''Class to implement a statsd gauge

    '''

    def send(self, subname, value):
        '''Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :keyword value: The gauge value to send
        '''
        name = self._get_name(self.name, subname)
        self.logger.info('%s: %d', name, value)
        return statsd.Client._send(self, {name: '%d|g' % value})
