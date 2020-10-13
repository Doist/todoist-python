# -*- coding: utf-8 -*-
#The OS module in python provides functions for interacting with the operating system. OS, comes under Python's standard utility modules.
import os

#Setuptools is a package development process library designed to facilitate packaging Python projects by enhancing the Python standard library distutils.
from setuptools import setup


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except Exception:
        return ""

#Internal Process
setup(
    name="todoist-python",
    version="8.1.2",
    packages=["todoist", "todoist.managers"],
    author="Doist Team",
    author_email="info@todoist.com",
    license="BSD",
    description="todoist-python - The official Todoist Python API library",
    long_description=read("README.md"),
    install_requires=[
        "requests", 
        "typing;python_version<'3.5'",
    ],
    # see here for complete list of classifiers
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=(
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
    ),
)
