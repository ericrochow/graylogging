#!/usr/bin/env python
# -*- coding: utf-8 -*-
from io import open
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

here = os.path.abspath(os.path.dirname(__file__))
about = {}

with open(
    os.path.join(here, "graylogging", "__version__.py"), mode="r", encoding="utf-8"
) as f:
    exec(f.read(), about)

with open("readme.rst", mode="r", encoding="utf-8") as f:
    readme = f.read()
with open("HISTORY.md", mode="r", encoding="utf-8") as f:
    history = f.read()

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine check dist/*")
    os.system("twine upload dist/*")
    sys.exit()


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        try:
            from multiprocessing import cpu_count

            self.pytest_args = ["-n", str(cpu_count()), "--boxed"]
        except (ImportError, NotImplementedError):
            self.pytest_args = ["-n", "1", "--boxed"]
        else:
            self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


test_requires = ["pytest", "pytest-mock"]
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
    tests_require=test_requires,
    url=about["__url__"],
    version=about["__version__"],
    zip_safe=False,
)
