DIR=$(shell pwd)
MYSOURCES=$(shell find punchbox -name "*.py" | tr "\n" " ")

ifeq (, $(shell which python3))
 $(error "No python3 installed, it is required. Make sure you also install python3 venv")
endif

##@ Available targets:

.DEFAULT_GOAL := help
.PHONY: all build lint test clean-package clean-pyc clean-test clean tox

all: clean build test lint package  ## rebuild everything from scratch with test, lint then generate a distribution

build: target/.distrib-built  ## install needed modules for development, tests, linting...

package: target/.distrib-package  ## generate the pex archive that will be used as distribution

lint: target/.distrib-lint  ## performs PEP257 and PEP8 code style checking and uses black for non opinionated code style with mypy static checking

test: target/.distrib-test  ## run tests quickly with the default Python

clean-package:  ## removed built distribution
	$(info ************  CLEANING DISTRIBUTION  ************)
	rm -rf dist
	rm -rf target
	-rm -rf target/.distrib-built

clean-pyc:  ## remove Python file artifacts
	$(info ************  CLEANING TEMPORARY FILES  ************)
	-find . -name '*.pyc' -exec rm -f {} +
	-find . -name '*.pyo' -exec rm -f {} +
	-find . -name '*~' -exec rm -f {} +
	-find . -name '__pycache__' -exec rm -fr {} +

clean-test:  ## remove all tests related cache
	$(info ************  CLEANING TEST REPORTS  ************)
	rm -fr .tox/
	rm -fr .coverage
	rm -fr htmlcov/
	rm -rf target/.distrib-tested
	rm -rf .pytest_cache
	rm -rf .mypy_cache

clean: clean-package clean-pyc clean-test  ## remove all build, test, coverage and Python artifacts
	$(info ************  CLEAN  ************)
	rm -rf target
	rm -rf .venv
	rm -rf dist
	rm -rf .cache

test-cli: target/.venv-created  ## run the punchbox cli
	@. ${DIR}/.venv/bin/activate && poetry run punchbox

tox: target/.venv-created  ## validate that application command group (dev only)
	@. ${DIR}/.venv/bin/activate && poetry run tox

target/.venv-created:
	$(info ************  CREATE PYTHON 3 .venv  VIRTUALENV  ************)
	mkdir -p target
	python3 -m venv .venv
	touch $@

target/.venv-dependencies: target/.venv-created pyproject.toml poetry.toml poetry.lock
	$(info ************  POETRY BUILD VIRTUALENV FROM SCRATCH WITH PEX INSIDE ************)
	mkdir -p target 
	@. ${DIR}/.venv/bin/activate && pip install -U setuptools wheel pip poetry
	# poetry at this step initializes the .venv with good version of pex and other dependencies
	@. ${DIR}/.venv/bin/activate && poetry install
	@. ${DIR}/.venv/bin/activate && poetry build
	touch $@

target/.distrib-built: target/.venv-created target/.venv-dependencies ${MYSOURCES}
	$(info ************  POETRY BUILD DISTRIBUTION AND UPDATE VIRTUALENV ************)
	$(echo MYSOURCES=${MYSOURCES})
	@. ${DIR}/.venv/bin/activate && poetry build
	touch $@

target/.distrib-lint: target/.venv-created
	$(info ************  Checking: code covertage, auto code formatting PEP8 PEP257 and static type  ************)
	@. ${DIR}/.venv/bin/activate && poetry run isort .
	@. ${DIR}/.venv/bin/activate && poetry run black .
	@. ${DIR}/.venv/bin/activate && poetry run flake8
	@. ${DIR}/.venv/bin/activate && poetry run mypy -p punchbox

target/.distrib-package: target/.venv-created  target/.distrib-built ${MYSOURCES}
	rm -rf dist
	@. ${DIR}/.venv/bin/activate && poetry run pex ${DIR} -c punchbox -o dist/pex/punchbox -v
	touch $@

target/.distrib-test: target/.venv-created
	$(info ************  Pytest Unit testing  ************)
	@. ${DIR}/.venv/bin/activate && poetry run pytest
	@. ${DIR}/.venv/bin/activate && poetry run pytest --cov=punchbox --cov-config .coveragerc tests/ -sq

##@ Helpers

.PHONY: help

help:  ## Display help menu
	@awk 'BEGIN {FS = ":.*##"; printf "\033[36m\033[0m\n"} /^[0-9a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
