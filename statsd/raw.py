"""Raw values.

Raw metrics bypass the statsd aggregation entirely and are passed
straight through to carbon with a timestamp. That makes them useful for
data that is already summarised, and cheap for data that would otherwise
cost far more in UDP headers than it does in payload.
"""

import time

from statsd.client import Client


class Raw(Client):
    """Class to implement a statsd raw message.
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
    >>> raw.send('name', 12435, time.time())
    True
    """

    def send(
        self,
        subname: str | None,
        value: object,
        timestamp: float | None = None,
    ) -> bool:
        """Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :keyword value: The raw value to send
        :keyword timestamp: The timestamp to send (defaults to current time)
        """
        ts: float
        if timestamp is None:
            ts = int(time.time())
        else:
            ts = timestamp
        name = self._get_name(self.name, subname)
        self.logger.info('%s: %s %s', name, value, ts)
        return self._send({name: f'{value}|r|{ts}'})
