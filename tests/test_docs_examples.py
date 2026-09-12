"""Execute every code sample in the README and the documentation.

Documentation that is never run is documentation that drifts. Each
``python`` fenced block in the README and in the docs pages is executed
here, in file order and in a shared namespace, so a sample may build on
the one above it exactly as a reader would expect.

A block that cannot run in the test environment, such as one importing a
web framework this package does not depend on, is preceded in the source
by ``<!-- docs-example: skip -->``. The page says so in prose as well, so
nobody mistakes an unexecuted block for a verified one.

The autouse ``udp_socket`` fixture from ``conftest.py`` applies here too,
so the samples exercise the real send path without a packet leaving the
process.
"""

import logging
import pathlib
import re
from collections.abc import Iterator
from typing import Any

import pytest
import statsd

PROJECT_ROOT = pathlib.Path(__file__).parent.parent
DOC_SOURCES: tuple[pathlib.Path, ...] = (
    PROJECT_ROOT / 'README.md',
    *sorted((PROJECT_ROOT / 'docs').glob('*.md')),
)
SKIP_MARKER = '<!-- docs-example: skip -->'
_PYTHON_BLOCK = re.compile(
    r'(?P<skip>' + re.escape(SKIP_MARKER) + r'\s*\n)?^```python\n'
    r'(?P<code>.*?)^```',
    re.MULTILINE | re.DOTALL,
)


def python_blocks(path: pathlib.Path) -> list[str]:
    """Return the runnable ``python`` fenced blocks of a Markdown file."""
    return [
        match.group('code')
        for match in _PYTHON_BLOCK.finditer(path.read_text())
        if not match.group('skip')
    ]


def skipped_blocks(path: pathlib.Path) -> list[str]:
    """Return the ``python`` blocks the page marks as not executed."""
    return [
        match.group('code')
        for match in _PYTHON_BLOCK.finditer(path.read_text())
        if match.group('skip')
    ]


def source_id(path: pathlib.Path) -> str:
    """Name a parametrised case after its path within the project."""
    return str(path.relative_to(PROJECT_ROOT))


@pytest.fixture
def sample_globals() -> Iterator[dict[str, Any]]:
    """Hand out a namespace and undo the global state a sample touches.

    ``Connection.set_defaults()`` writes to class attributes and
    ``logging.basicConfig()`` writes to the root logger, both of which
    outlive the sample that called them.
    """
    connection = statsd.Connection
    defaults = (
        connection.default_host,
        connection.default_port,
        connection.default_sample_rate,
        connection.default_disabled,
    )
    level = logging.getLogger().level

    yield {'__name__': 'docs_example'}

    (
        connection.default_host,
        connection.default_port,
        connection.default_sample_rate,
        connection.default_disabled,
    ) = defaults
    logging.getLogger().setLevel(level)


@pytest.mark.parametrize('path', DOC_SOURCES, ids=source_id)
def test_doc_samples_execute(
    path: pathlib.Path,
    sample_globals: dict[str, Any],
) -> None:
    blocks = python_blocks(path)
    assert blocks, f'no runnable python samples found in {source_id(path)}'

    for number, block in enumerate(blocks, start=1):
        code = compile(block, f'{source_id(path)}:block {number}', 'exec')
        exec(code, sample_globals)


@pytest.mark.parametrize('path', DOC_SOURCES, ids=source_id)
def test_skipped_samples_are_declared(path: pathlib.Path) -> None:
    """A skipped block has to be at least syntactically valid Python.

    The marker excuses a block from running, not from being correct. This
    still catches a typo in a snippet a reader is going to copy.
    """
    for number, block in enumerate(skipped_blocks(path), start=1):
        compile(block, f'{source_id(path)}:skipped block {number}', 'exec')
