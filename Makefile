
PWD = $(shell pwd)
VENV ?= $(PWD)/.venv
INSTALL_DIR ?= /usr/local/bin

PATH := $(VENV)/bin:$(shell printenv PATH)
SHELL := env PATH=$(PATH) /bin/bash

.PHONY: build

$(VENV):
	virtualenv $(VENV)
	$(VENV)/bin/pip install -r dev-requirements.txt

build: $(VENV)
	python setup.py sdist install

watch:
	while sleep 1; do \
		find aws_sudo \
		| entr -d $(MAKE) unittest lint build; \
	done

unittest: $(VENV)
	python -m unittest discover aws_sudo

test: $(VENV)
	cd tests && ./run

install:
	ln -s $(PWD)/.venv/bin/awssudo $(INSTALL_DIR)/awssudo
	@echo "awssu installed in $(INSTALL_DIR)/awssudo"

upload: $(VENV)
	twine upload dist/*
	# python setup.py sdist upload -r pypi

lint: $(VENV)
	pep8 aws_sudo/

clean:
	rm -rf .venv
	rm -rf build
	rm -rf aws_sudo.egg-info
	rm -rf dist
