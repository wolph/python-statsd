import importlib.metadata

project = 'python-statsd'
author = 'Rick van Hattem (Wolph)'
copyright = '2011-2026, Rick van Hattem (Wolph)'

release = importlib.metadata.version('python-statsd')
version = '.'.join(release.split('.')[:2])

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

html_theme = 'furo'

exclude_patterns = ['_build']
