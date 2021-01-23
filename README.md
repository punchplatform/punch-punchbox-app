# the PunchBox

Welcome to the punchbox tool. This project is an attempt to come up with a  successor the 
https://github.com/punchplatform/punchbox project. In short, a tool to easily deploy kast or punch instances.

This project uses [poetry](https://python-poetry.org/) as it's dependency manager and PEX for distribution.

## Prerequisites

Before proceeding, you should have `python == 3.6.8` installed correctly. If you are using `pyenv`, make sure to have 
this version of python installed:

```shell
pyenv install 3.6.8
```

## How To

The Makefile is explicit simply type 'make' to see the options. STart simply with:

```shell
make all
```

That generates the punchbox executable tool in  ./dist/pex/punchbox.
From there use the tool inline documentation to understand how it works. 

Note that a variant to run the punchbox is to pass through poetry:

```shell
source .venv/bin/activate
poetry run punchbox
```

