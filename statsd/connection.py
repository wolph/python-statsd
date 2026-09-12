"""The UDP connection to the statsd server.

A connection is a fire-and-forget UDP socket with an optional sample
rate. Nothing is ever read back, and a failing send is logged rather
than raised, because losing a metric should not take an application
down with it. Process-wide defaults live in
:meth:`Connection.set_defaults`.
"""

import logging
import random
import socket


class Connection:
    """Statsd Connection

    :keyword host: The statsd host to connect to, defaults to `localhost`
    :type host: str
    :keyword port: The statsd port to connect to, defaults to `8125`
    :type port: int
    :keyword sample_rate: The sample rate, defaults to `1` (meaning always)
    :type sample_rate: float
    :keyword disabled: Turn off sending UDP packets, defaults to ``False``
    :type disabled: bool
    """

    default_host: str = 'localhost'
    default_port: int = 8125
    default_sample_rate: float = 1
    default_disabled: bool = False

    @classmethod
    def set_defaults(
        cls,
        host: str = 'localhost',
        port: int = 8125,
        sample_rate: float = 1,
        disabled: bool = False,
    ) -> None:
        """Set the defaults for every connection created after this call

        The values are stored on the class, so connections that already
        exist keep the settings they were built with. Call this once
        during startup, before the application creates its clients.

        :keyword host: The statsd host to connect to
        :type host: str
        :keyword port: The statsd port to connect to
        :type port: int
        :keyword sample_rate: The sample rate, `1` meaning always
        :type sample_rate: float
        :keyword disabled: Turn off sending UDP packets
        :type disabled: bool
        """
        cls.default_host = host
        cls.default_port = port
        cls.default_sample_rate = sample_rate
        cls.default_disabled = disabled

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        sample_rate: float | None = None,
        disabled: bool | None = None,
    ) -> None:
        self._host: str = host or self.default_host
        self._port: int = int(port or self.default_port)
        self._sample_rate: float = sample_rate or self.default_sample_rate
        self._disabled: bool = disabled or self.default_disabled
        self.logger: logging.Logger = logging.getLogger(
            f'{__name__}.{type(self).__name__}'
        )
        self.udp_sock: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM
        )
        self.udp_sock.connect((self._host, self._port))
        self.logger.debug(
            'Initialized connection to %s:%d with P(%.1f)',
            self._host,
            self._port,
            self._sample_rate,
        )

    def send(
        self,
        data: dict[str, object],
        sample_rate: float | None = None,
    ) -> bool:
        """Send the data over UDP while taking the sample_rate in account

        The sample rate should be a number between `0` and `1` which
        indicates the probability that a message will be sent. The
        sample_rate is also communicated to `statsd` so it knows what
        multiplier to use.

        :keyword data: The data to send
        :type data: dict
        :keyword sample_rate: The sample rate, defaults to `1`
            (meaning always)
        :type sample_rate: float
        """
        if self._disabled:
            self.logger.debug('Connection disabled, not sending data')
            return False

        if sample_rate is None:
            sample_rate = self._sample_rate

        sampled_data: dict[str, object] = {}
        if sample_rate < 1:
            if random.random() <= sample_rate:
                # Modify the data so statsd knows our sample_rate
                for stat, value in data.items():
                    sampled_data[stat] = f'{value}|@{sample_rate}'
        else:
            sampled_data = data

        try:
            for stat, value in sampled_data.items():
                self.udp_sock.send(f'{stat}:{value}'.encode())
        except OSError:
            self.logger.exception('unexpected error while sending data')
            return False
        return True

    def __del__(self) -> None:
        # Close the UDP socket explicitly for pypy; guarded because
        # __del__ also runs when __init__ failed before creating it.
        udp_sock: socket.socket | None = getattr(self, 'udp_sock', None)
        if udp_sock is not None:
            udp_sock.close()

    def __repr__(self) -> str:
        return (
            f'<{type(self).__name__}[{self._host}:{self._port}]'
            f' P({self._sample_rate:.1f})>'
        )
