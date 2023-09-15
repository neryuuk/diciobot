#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=unused-argument, wrong-import-position
"""
O diciobot consulta o [Dicio - Dicionário Online de Português],
composto por definições, significados, exemplos e rimas
que caracterizam mais de 400.000 palavras e verbetes.

See:
https://github.com/neryuuk/diciobot
https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools
"""

from pathlib import Path
from setuptools import setup, find_packages

long_description = (
    Path(__file__).parent.resolve() / "README.md"
).read_text(encoding="utf-8")

setup(
    name="diciobot",
    version="2.0.0",
    description="A portuguese thesaurus bot for Telegram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neryuuk/diciobot",
    author="Nelson Antunes",
    author_email="neryuuk@neryuuk.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: Free For Educational Use",
        "Natural Language :: Portuguese (Brazilian)",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="telegram, bot, portuguese, thesaurus",  # Optional
    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=find_packages(where="source"),  # Required
    python_requires=">=3.7, <4",
    install_requires=[
        "lxml", "python-dotenv", "python-telegram-bot", "redis", "Requests"
    ],
    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
    project_urls={
        "Bug Reports": "https://github.com/neryuuk/diciobot/issues",
        "Source": "https://github.com/neryuuk/diciobot/",
        "Thanks": "https://t.me/neryuuk",
    },
)
