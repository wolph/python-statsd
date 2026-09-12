"""Metric name handling and client construction.

:class:`Client` owns the dotted metric name and the
:class:`~statsd.connection.Connection` that carries it, and every metric
type in this package builds on it. Sub-clients are created through
:meth:`Client.get_client`, which appends to the name and can switch to a
different metric type at the same time.
"""

import logging
from typing import TYPE_CHECKING, TypeVar, overload

from statsd.connection import Connection

if TYPE_CHECKING:
    from statsd.average import Average
    from statsd.counter import Counter
    from statsd.gauge import Gauge
    from statsd.raw import Raw
    from statsd.timer import Timer

_C = TypeVar('_C', bound='Client')


class Client:
    """Statsd Client Object

    :keyword name: The name for this client
    :type name: str
    :keyword connection: The connection to use, will be automatically
        created if not given
    :type connection: :class:`~statsd.connection.Connection`

    >>> client = Client('test')
    >>> client
    <Client:test@<Connection[localhost:8125] P(1.0)>>
    >>> client.get_client('spam')
    <Client:test.spam@<Connection[localhost:8125] P(1.0)>>
    """

    def __init__(
        self,
        name: str | bytes,
        connection: Connection | None = None,
    ) -> None:
        #: The name of the client, everything sent from this client will
        #: be prefixed by name
        self.name: str = self._get_name(name)
        if not connection:
            connection = Connection()
        #: The :class:`~statsd.connection.Connection` to use
        self.connection: Connection = connection
        self.logger: logging.Logger = logging.getLogger(
            f'{__name__}.{type(self).__name__}'
        )

    @classmethod
    def _get_name(cls, *name_parts: str | bytes | None) -> str:
        parts: list[str] = []
        for part in name_parts:
            if isinstance(part, bytes):
                part = part.decode('utf-8', 'replace')
            if part:
                parts.append(part)
        return '.'.join(parts)

    @overload
    def get_client(
        self,
        name: str | None = None,
        class_: None = None,
    ) -> 'Client': ...

    @overload
    def get_client(
        self,
        name: str | None = None,
        *,
        class_: type[_C],
    ) -> _C: ...

    @overload
    def get_client(self, name: str | None, class_: type[_C]) -> _C: ...

    def get_client(
        self,
        name: str | None = None,
        class_: type[_C] | None = None,
    ) -> '_C | Client':
        """Get a (sub-)client with a separate namespace

        This way you can create a global/app based client which creates
        subclients per class/function

        :keyword name: The name to use, if the name for this client was
            `spam` and the `name` argument is `eggs` than the resulting
            name will be `spam.eggs`
        :type name: str
        :keyword class_: The :class:`~statsd.client.Client` subclass to
            use (e.g. :class:`~statsd.timer.Timer` or
            :class:`~statsd.counter.Counter`)
        :type class_: :class:`~statsd.client.Client`
        """
        name = self._get_name(self.name, name)
        if class_ is None:
            return type(self)(name=name, connection=self.connection)
        return class_(name=name, connection=self.connection)

    def get_average(self, name: str | None = None) -> 'Average':
        """Shortcut for getting an :class:`~statsd.average.Average`
        instance

        :keyword name: See :func:`~statsd.client.Client.get_client`
        :type name: str
        """
        from statsd.average import Average

        return self.get_client(name=name, class_=Average)

    def get_counter(self, name: str | None = None) -> 'Counter':
        """Shortcut for getting a :class:`~statsd.counter.Counter`
        instance

        :keyword name: See :func:`~statsd.client.Client.get_client`
        :type name: str
        """
        from statsd.counter import Counter

        return self.get_client(name=name, class_=Counter)

    def get_gauge(self, name: str | None = None) -> 'Gauge':
        """Shortcut for getting a :class:`~statsd.gauge.Gauge` instance

        :keyword name: See :func:`~statsd.client.Client.get_client`
        :type name: str
        """
        from statsd.gauge import Gauge

        return self.get_client(name=name, class_=Gauge)

    def get_raw(self, name: str | None = None) -> 'Raw':
        """Shortcut for getting a :class:`~statsd.raw.Raw` instance

        :keyword name: See :func:`~statsd.client.Client.get_client`
        :type name: str
        """
        from statsd.raw import Raw

        return self.get_client(name=name, class_=Raw)

    def get_timer(self, name: str | None = None) -> 'Timer':
        """Shortcut for getting a :class:`~statsd.timer.Timer` instance

        :keyword name: See :func:`~statsd.client.Client.get_client`
        :type name: str
        """
        from statsd.timer import Timer

        return self.get_client(name=name, class_=Timer)

    def __repr__(self) -> str:
        return f'<{type(self).__name__}:{self.name}@{self.connection!r}>'

    def _send(self, data: dict[str, object]) -> bool:
        return self.connection.send(data)
