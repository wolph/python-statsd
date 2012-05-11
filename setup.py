import os
from setuptools import setup

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = 'See http://pypi.python.org/pypi/python-statsd/'

setup(
    name = 'python-statsd',
    version = '1.5.1',
    author = 'Rick van Hattem',
    author_email = 'Rick.van.Hattem@Fawo.nl',
    description = '''statsd is a client for Etsy's node-js statsd server. 
        A proxy for the Graphite stats collection and graphing server.''',
    url='https://github.com/WoLpH/python-statsd',
    license = 'BSD',
    packages=['statsd'],
    long_description=long_description,
    test_suite='nose.collector',
    setup_requires=['nose'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)
