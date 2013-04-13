import statsd


class Average(statsd.Client):
    '''Class to implement a statsd "average" message.
    This value will be averaged against other messages before being
    sent.

    See https://github.com/chuyskywalker/statsd/blob/master/README.md for
    more info.

    >>> average = Average('application_name')
    >>> # do something here
    >>> average.send('subname', 123)
    True
    '''

    def send(self, subname, value):
        '''Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :keyword value: The raw value to send
        '''
        name = self._get_name(self.name, subname)
        self.logger.info('%s: %d', name, value)
        return statsd.Client._send(self, {name: '%d|a' % value})

