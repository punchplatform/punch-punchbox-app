DIR=$(shell pwd)
MYSOURCES=$(shell find punchbox -name "*.py" | tr "\n" " ")

ifeq (, $(shell which python3))
 $(error "No python3 installed, it is required. Make sure you also install python3 venv")
endif


help:
	@echo "all                       - rebuild everything from scratch with test and lint"
	@echo "clean                     - remove all build, test, coverage and Python artifacts"
	@echo "clean-pyc                 - remove Python file artifacts"
	@echo "clean-test                - remove test and coverage artifacts"
	@echo "build                     - generate source tar.gz, wheel and pex distributions"
	@echo "test               		 - run tests quickly with the default Python"

all: clean build test

build: target/.distrib-built

test: target/.distrib-tested

clean-package:
	$(info ************  CLEANING DISTRIBUTION  ************)
	rm -rf dist
	rm -rf target
	-rm -rf target/.distrib-built

clean-pyc:
	$(info ************  CLEANING TEMPORARY FILES  ************)
	-find . -name '*.pyc' -exec rm -f {} +
	-find . -name '*.pyo' -exec rm -f {} +
	-find . -name '*~' -exec rm -f {} +
	-find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	$(info ************  CLEANING TEST REPORTS  ************)
	rm -fr .tox/
	rm -fr .coverage
	rm -fr htmlcov/
	rm -rf target/.distrib-tested

clean: clean-package clean-pyc clean-test
	$(info ************  CLEAN  ************)
	rm -rf target
	rm -rf .venv
	rm -rf dist
	rm -rf .cache

test-cli:
	@. ${DIR}/.venv/bin/activate && poetry run punchbox

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
	rm -rf dist
	@. ${DIR}/.venv/bin/activate && poetry build
	@. ${DIR}/.venv/bin/activate && poetry run pex ${DIR} -c punchbox -o dist/pex/punchbox -v
	touch $@

target/.distrib-tested: target/.venv-created target/.distrib-built
	$(info ************  POETRY TEST  ************)
	@. ${DIR}/.venv/bin/activate && poetry run flake8
	@. ${DIR}/.venv/bin/activate && poetry run black punchbox
	@. ${DIR}/.venv/bin/activate && poetry run mypy -p punchbox --python-version 3.6 --ignore-missing
	touch $@
