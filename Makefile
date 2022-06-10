# :Author: Lance Finn Helsten <lanhel@flyingtitans.com>
# :Copyright: Copyright (C) 2022 Lance Finn Helsten
.POSIX:

BUILDDIR      = ${PWD}/build
SETUP         = python -m setup
SETUPFLAGS    =
PIP           = python -m pip
PIPFLAGS      = 


.PHONY: install
install:			## Install system
	${SETUP} ${SETUPFLAGS} install


# Publish requires a username & password for twine to upload to PyPI
# ``export TWINE_USERNAME=<username>``
# ``export TWINE_PASSWORD=<password>``
#
# For automated upload with API token the following is required:
# ``export TWINE_USERNAME=__token__``
# ``export TWINE_PASSWORD=pypi-<token_value>``
.PHONY: publish
publish: clean		## Publish the library to the central PyPi repository
	${SETUP} ${SETUPFLAGS} sdist bdist_wheel
	python -m twine check dist/*
	python -m twine upload --verbose dist/*
	@$(MAKE) -C docs publish


.PHONY: docker
docker: 			## Build docker containers
	@mkdir -p ${BUILDDIR}/docker
	@$(MAKE) -C src/docker PROJDIR=${PWD} BUILDDIR=${BUILDDIR}/docker docker


.PHONY: docs
docs:				## Create documentation
	@echo Create documentation
	@$(MAKE) -C docs docs


.PHONY: validate
validate: lint test	## Validate project for CI, CD, and publish


clean:				## Clean generated files
	@rm -rf ${BUILDDIR}
	@rm -rf dist
	@rm -rf sdist
	@rm -rf var
	@rm -rf tmp
	@rm -rf .eggs
	@rm -rf *.egg-info
	@rm -rf .coverage
	@rm -rf pip-wheel-metadata
	@find src -name '__pycache__' -exec rm -rf {} \; -prune
	@find tests -name '__pycache__' -exec rm -rf {} \; -prune
	@$(MAKE) -C docs clean


clean_cache:		## Clean caches
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@rm -rf coverage_html_report
	@rm -rf .mypy_cache
	@rm -rf .hypothesis


.PHONY: build
build:				## Build into ``./build`` directory
	${SETUP} ${SETUPFLAGS} build


.PHONY: test
test:				## Run test suite
test: build
	pytest --cov=atm
	coverage html


.PHONY: lint
lint:				## Check source for conformance
	@echo Checking source conformance
	black --check setup.py src tests
	pylint -f parseable -r n src
	pycodestyle src
	pydocstyle src
	mypy src


updatedev:			## Update / init all packages for development environment
	${PIP} ${PIPFLAGS} install --upgrade pip setuptools wheel twine
	${PIP} ${PIPFLAGS} install --upgrade --editable .
	${PIP} ${PIPFLAGS} install --upgrade --editable ".[dev]"
	${PIP} ${PIPFLAGS} install --upgrade --editable ".[lint]"
	${PIP} ${PIPFLAGS} install --upgrade --editable ".[tests]"
	${PIP} ${PIPFLAGS} install --upgrade --editable ".[docs]"

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

