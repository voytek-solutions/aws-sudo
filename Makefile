
PWD = $(shell pwd)

PATH := $(PWD)/.venv/bin:$(shell printenv PATH)
SHELL := env PATH=$(PATH) /bin/bash

.PHONY: build

.venv:
	virtualenv .venv
	.venv/bin/pip install pep8 twine

build: .venv
	python setup.py install

watch:
	while sleep 1; do \
		find aws_sudo \
		| entr -d $(MAKE) unittest lint build; \
	done

unittest:
	python -m unittest discover aws_sudo

install:
	ln -s $(PWD)/.venv/bin/awssudo /usr/local/bin/awssudo
	@echo "awssu installed in /usr/local/bin/awssudo"

upload:
	twine upload dist/*

lint:
	pep8 aws_sudo/

clean:
	rm -rf .venv
