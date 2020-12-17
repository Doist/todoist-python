# -*- coding: utf-8 -*-
import os

from setuptools import setup


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except Exception:
        return ""


setup(
    name="todoist-python",
    version="8.1.3",
    packages=["todoist", "todoist.managers"],
    author="Doist Team",
    author_email="integrations@todoist.com",
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
