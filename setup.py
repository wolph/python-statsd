import os
import statsd
import setuptools

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = 'See http://pypi.python.org/pypi/python-statsd/'

tests_require = [
    'nose',
    'coverage',
    'mock',
]

docs_require = [
    'changelog',
    'sphinx>=1.5.0',
]

setuptools.setup(
    name=statsd.__package_name__,
    version=statsd.__version__,
    author=statsd.__author__,
    author_email=statsd.__author_email__,
    description=statsd.__description__,
    url=statsd.__url__,
    license='BSD',
    packages=setuptools.find_packages(exclude=('docs', 'tests',)),
    long_description=long_description,
    test_suite='nose.collector',
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
    extras_require={
        'docs': docs_require,
        'tests': tests_require,
    },
)

