from   __future__ import unicode_literals
import os.path
import sys

sys.path.insert(0, os.path.abspath('..'))
from   doapi import __version__

project   = 'doapi'
author    = 'John T. Wodder II'
copyright = '2015-2016 John T. Wodder II'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]

autodoc_default_flags = ['members', 'undoc-members']
# NOTE: Do not set 'inherited-members', as it will cause all of the
# MutableMapping methods to be listed under each & every resource.
autodoc_member_order = 'bysource'

intersphinx_mapping = {
    "python": ("https://docs.python.org/2.7", None),
    "requests": ("http://docs.python-requests.org/en/latest", None),
    "simplejson": ("http://simplejson.readthedocs.org/en/latest", None),
}

exclude_patterns = ['_build']
source_suffix = '.rst'
source_encoding = 'utf-8-sig'
master_doc = 'index'
version = __version__
release = __version__
today_fmt = '%Y %b %d'
default_role = 'py:obj'
pygments_style = 'sphinx'
todo_include_todos = True

html_theme = 'sphinx_rtd_theme'
html_last_updated_fmt = '%Y %b %d'
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True
