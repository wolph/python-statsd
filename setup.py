import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'python-statsd',
    version = '1.1',
    author = 'Rick van Hattem',
    author_email = 'Rick.van.Hattem@Fawo.nl',
    description = '''statsd is a client for Etsy's node-js statsd server. 
        A proxy for the Graphite stats collection and graphing server.''',
    url='https://github.com/WoLpH/python-statsd',
    license = 'BSD',
    packages=['statsd'],
    long_description=read('README.rst'),
    test_suite='nose.collector',
    setup_requires=['nose'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)
