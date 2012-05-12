import os
import statsd
from setuptools import setup

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = 'See http://pypi.python.org/pypi/python-statsd/'

setup(
    name=statsd.__name__,
    version=statsd.__version__,
    author=statsd.__author__,
    author_email=statsd.__author_email__,
    description=statsd.__description__,
    url=statsd.__url__,
    license='BSD',
    packages=['statsd'],
    long_description=long_description,
    test_suite='nose.collector',
    setup_requires=['nose', 'mock'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)

