"""
Compatability library for python2 and python3 support.
"""
import sys
import decimal

PY3K = sys.version_info >= (3, 0)

def iter_dict(dict):
    if PY3K:
        return dict.items()
    else:
        return dict.iteritems()


def to_str(value):
    if PY3K and isinstance(value, bytes):  # pragma: no cover
        value = value.encode('utf-8', 'replace')
    elif not PY3K and isinstance(value, unicode):
        value = value.encode('utf-8', 'replace')
    return value

if PY3K:
    NUM_TYPES = int, float, decimal.Decimal
else:
    NUM_TYPES = int, long, float, decimal.Decimal
