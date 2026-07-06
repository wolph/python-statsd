from unittest import mock

import pytest
import statsd


@pytest.fixture
def client() -> statsd.Client:
    return statsd.Client('testing')


def test_client_repr(client: statsd.Client) -> None:
    assert repr(client) == (
        '<Client:testing@<Connection[localhost:8125] P(1.0)>>'
    )


def test_get_client_inherits_connection_and_name(
    client: statsd.Client,
) -> None:
    sub = client.get_client('spam')
    assert sub.name == 'testing.spam'
    assert sub.connection is client.connection
    assert type(sub) is statsd.Client


def test_get_client_keeps_own_class() -> None:
    timer = statsd.Timer('testing')
    sub = timer.get_client('spam')
    assert type(sub) is statsd.Timer
    assert sub.name == 'testing.spam'


def test_get_client_with_class(client: statsd.Client) -> None:
    sub = client.get_client('spam', class_=statsd.Counter)
    assert type(sub) is statsd.Counter
    assert sub.name == 'testing.spam'


@pytest.mark.parametrize(
    ('shortcut', 'expected_class'),
    [
        ('get_average', statsd.Average),
        ('get_counter', statsd.Counter),
        ('get_gauge', statsd.Gauge),
        ('get_raw', statsd.Raw),
        ('get_timer', statsd.Timer),
    ],
)
def test_shortcuts(
    client: statsd.Client,
    shortcut: str,
    expected_class: type[statsd.Client],
) -> None:
    sub = getattr(client, shortcut)('spam')
    assert type(sub) is expected_class
    assert sub.name == 'testing.spam'
    assert sub.connection is client.connection


def test_default_connection() -> None:
    client = statsd.Client('testing')
    assert isinstance(client.connection, statsd.Connection)


def test_explicit_connection() -> None:
    connection = statsd.Connection(disabled=True)
    client = statsd.Client('testing', connection)
    assert client.connection is connection


def test_get_name_joins_and_skips_empty() -> None:
    assert statsd.Client._get_name('spam', 'eggs') == 'spam.eggs'
    assert statsd.Client._get_name('spam', None, '') == 'spam'
    assert statsd.Client._get_name() == ''


def test_get_name_decodes_bytes() -> None:
    assert statsd.Client._get_name(b'spam', 'eggs') == 'spam.eggs'
    assert statsd.Client._get_name(b'\xff') == '�'


def test_bytes_client_name() -> None:
    assert statsd.Client(b'testing').name == 'testing'


def test_send_uses_connection(
    client: statsd.Client, udp_socket: mock.MagicMock
) -> None:
    assert client._send({'testing.spam': '1|c'}) is True
    udp_socket.send.assert_called_once_with(b'testing.spam:1|c')
