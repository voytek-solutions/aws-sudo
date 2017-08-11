
PWD = $(shell pwd)
VENV ?= .venv

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

install:
	ln -s $(PWD)/.venv/bin/awssudo /usr/local/bin/awssudo
	@echo "awssu installed in /usr/local/bin/awssudo"

upload: $(VENV)
	twine upload dist/*
	# python setup.py sdist upload -r pypi

lint: $(VENV)
	pep8 aws_sudo/

clean:
	rm -rf .venv
