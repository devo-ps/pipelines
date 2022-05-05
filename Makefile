#!/usr/bin/make
# WARN: gmake syntax
########################################################
# Makefile for Ansible message bus worker
#
# useful targets:
#   make tests ---------------- run the test
#   make pyflakes, make pep8 -- source code checks

########################################################
# variable section
PY := python3
VENV := .venv
VENV_BIN := ${VENV}/bin

API_SERVER_ARGS := server --workspace=test/fixtures/workspace --host 0.0.0.0

NOSETESTS := ${VENV_BIN}/nosetests
PYFLAKES := ${VENV_BIN}/pyflakes

-include local.mk

NAME = "pipelines"
OS = $(shell uname -s)


.PHONY: test

${VENV}:
	python3 -m venv ${VENV}

install: ${VENV}
	${VENV}/bin/pip install -U pip
	${VENV}/bin/pip install -U pipenv
	${VENV}/bin/pipenv install

run:
	${VENV}/bin/python -m pipelines ${API_SERVER_ARGS}

test:
	# PYTHONPATH=./pipelines $(NOSETESTS) -d -v -w test/*
	PYTHONPATH=. $(NOSETESTS) -d -v -w test

pep8:
	@echo "#############################################"
	@echo "# Running PEP8 Compliance Tests"
	@echo "#############################################"
	${VENV_BIN}/pep8 -r --ignore=E501,E221,W291,W391,E302,E251,E203,W293,E231,E303,E201,E225,E261,E241 bin/ pipelines/

pyflakes:
	${PYFLAKES} test/*/*.py pipelines/*py pipelines/*/*py bin/*

sync-requirements:
	${VENV_BIN}/pipenv-setup sync
	${VENV_BIN}/autopep8 -i -a -a setup.py
