import os
import setuptools

# To prevent importing about and thereby breaking the coverage info we use this
# exec hack
about = {}
with open('statsd/__about__.py') as fp:
    exec(fp.read(), about)

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

if __name__ == '__main__':
    setuptools.setup(
        name=about['__package_name__'],
        version=about['__version__'],
        author=about['__author__'],
        author_email=about['__author_email__'],
        description=about['__description__'],
        url=about['__url__'],
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

