"""Shared pytest fixtures.

The autouse ``udp_socket`` fixture replaces ``socket.socket`` for every
test (including ``--doctest-modules`` doctests), so ``Connection`` runs
its real ``send`` logic against a fake socket and nothing ever reaches
the network.
"""

from collections.abc import Iterator
from unittest import mock

import pytest


@pytest.fixture(autouse=True)
def udp_socket() -> Iterator[mock.MagicMock]:
    with mock.patch('socket.socket', autospec=True) as socket_class:
        yield socket_class.return_value
