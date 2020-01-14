#!/usr/bin/env python
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

autoclass_content = "both"
autodoc_default_flags = [
    "inherited-members",
    "members",
    "private-members",
    "show-inheritence",
]

extensions = ["sphinx.ext.autodoc", "sphinx.ext.autosummary", "sphinx.ext.napoleon"]

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_rtype = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False

html_theme = "sphinx_rtd_theme"
