import logging
import statsd

from . import compat


class Client(object):

    '''Statsd Client Object

    :keyword name: The name for this client
    :type name: str
    :keyword connection: The connection to use, will be automatically created
        if not given
    :type connection: :class:`~statsd.connection.Connection`

    >>> client = Client('test')
    >>> client
    <Client:test@<Connection[localhost:8125] P(1.0)>>
    >>> client.get_client('spam')
    <Client:test.spam@<Connection[localhost:8125] P(1.0)>>
    '''

    #: The name of the client, everything sent from this client will be \
    #: prefixed by name
    name = None

    #: The :class:`~statsd.connection.Connection` to use, creates a new
    #: connection if no connection is given
    connection = None

    def __init__(self, name, connection=None):
        self.name = self._get_name(name)
        if not connection:
            connection = statsd.Connection()
        self.connection = connection
        self.logger = logging.getLogger(
            '%s.%s' % (__name__, self.__class__.__name__))

    @classmethod
    def _get_name(cls, *name_parts):
        name_parts = [compat.to_str(x) for x in name_parts if x]
        return '.'.join(name_parts)

    def get_client(self, name=None, class_=None):
        '''Get a (sub-)client with a separate namespace
        This way you can create a global/app based client with subclients
        per class/function

        :keyword name: The name to use, if the name for this client was `spam`
            and the `name` argument is `eggs` than the resulting name will be
            `spam.eggs`
        :type name: str
        :keyword class_: The :class:`~statsd.client.Client` subclass to use
            (e.g. :class:`~statsd.timer.Timer` or
            :class:`~statsd.counter.Counter`)
        :type class_: :class:`~statsd.client.Client`
        '''

        # If the name was given, use it. Otherwise simply clone
        name = self._get_name(self.name, name)

        # Create using the given class, or the current class
        if not class_:
            class_ = self.__class__

        return class_(
            name=name,
            connection=self.connection,
        )

    def get_average(self, name=None):
        '''Shortcut for getting an :class:`~statsd.average.Average` instance

        :keyword name: See :func:`~statsd.client.Client.get_client`
        :type name: str
        '''
        return self.get_client(name=name, class_=statsd.Average)

    def get_counter(self, name=None):
        '''Shortcut for getting a :class:`~statsd.counter.Counter` instance

        :keyword name: See :func:`~statsd.client.Client.get_client`
        :type name: str
        '''
        return self.get_client(name=name, class_=statsd.Counter)

    def get_gauge(self, name=None):
        '''Shortcut for getting a :class:`~statsd.gauge.Gauge` instance

        :keyword name: See :func:`~statsd.client.Client.get_client`
        :type name: str
        '''
        return self.get_client(name=name, class_=statsd.Gauge)

    def get_raw(self, name=None):
        '''Shortcut for getting a :class:`~statsd.raw.Raw` instance

        :keyword name: See :func:`~statsd.client.Client.get_client`
        :type name: str
        '''
        return self.get_client(name=name, class_=statsd.Raw)

    def get_timer(self, name=None):
        '''Shortcut for getting a :class:`~statsd.timer.Timer` instance

        :keyword name: See :func:`~statsd.client.Client.get_client`
        :type name: str
        '''
        return self.get_client(name=name, class_=statsd.Timer)

    def __repr__(self):
        return '<%s:%s@%r>' % (
            self.__class__.__name__,
            self.name,
            self.connection,
        )

    def _send(self, data):
        return self.connection.send(data)
