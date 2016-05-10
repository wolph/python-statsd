'''
Compatibility library for python2 and python3 support.
'''
import sys
import decimal

PY3K = sys.version_info >= (3, 0)


def iter_dict(dict_):  # pragma: no cover
    if PY3K:
        return dict_.items()
    else:
        return dict_.iteritems()


def to_str(value):  # pragma: no cover
    if PY3K and isinstance(value, bytes):
        value = value.encode('utf-8', 'replace')
    elif not PY3K and isinstance(value, unicode):
        value = value.encode('utf-8', 'replace')
    return value

if PY3K:  # pragma: no cover
    NUM_TYPES = int, float, decimal.Decimal
else:  # pragma: no cover
    NUM_TYPES = int, long, float, decimal.Decimal
