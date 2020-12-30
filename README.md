# the PunchBox

Welcome to the punhcbox tool. This project is the successor of the 
https://github.com/punchplatform/punchbox project. We plan to make it
the official tool to deploy various sort of punch: standalone, production,
or even hybrids. 

This project uses [poetry](https://python-poetry.org/) as it's dependency manager and PEX for distribution.

## Prerequisites

Before proceeding, you should have `python == 3.6.8` installed correctly. If you are using `pyenv`, make sure to have 
this version of python installed:

```shell
pyenv install 3.6.8
```

## Workflow

Use the provided `Makefile` to start a clean development environment.

```shell
# Run punchbox in development mode

source .venv/bin/activate
poetry run punchbox

# or

make test-cli

# After each modification be sure to run
make lint

# Before pushing
make all
```
