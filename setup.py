#!/usr/bin/env python
# -*- coding: utf-8 -*-
from io import open
import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
about = {}

with open(
    os.path.join(here, "graylogging", "__version__.py"), mode="r", encoding="utf-8"
) as f:
    exec(f.read(), about)

with open("README.md", mode="r", encoding="utf-8") as f:
    readme = f.read()
with open("HISTORY.md", mode="r", encoding="utf-8") as f:
    history = f.read()

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine check dist/*")
    os.system("twine upload dist/*")
    sys.exit()


packages = find_packages(exclude=["tests"])

setup(
    author=about["__author__"],
    author_email=about["__author_email__"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description=about["__description__"],
    extras_require={"docs": ["Sphinx", "SimpleHTTPServer", "sphinx_rtd_theme"]},
    install_requires=["requests[security]"],
    long_description=readme,
    long_description_content_type="text/markdown",
    name=about["__title__"],
    packages=packages,
    package_dir={"graylogging": "graylogging"},
    python_requires=">=3.6",
    url=about["__url__"],
    version=about["__version__"],
    zip_safe=False,
)
