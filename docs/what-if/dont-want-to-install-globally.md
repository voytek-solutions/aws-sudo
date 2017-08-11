# What If I Don't Want to Install `awssu` Globally

You can add `awssu` as a dependency to your project using virtualenv.

One simple way for doing that is to use this example Makefile:

```
PROFILE ?=
PWD = $(shell pwd)
PATH := $(PWD)/.venv/bin:$(shell printenv PATH)
SHELL := env PATH=$(PATH) /bin/bash

ifneq ($(PROFILE),)
export AWS_DEFAULT_PROFILE=$(PROFILE)
export AWS_PROFILE=$(PROFILE)
endif

## Assumes role (profile) and udpates ~/.aws/credentials
# Usage:
#   make awssu
#   make awssu PROFILE=myproject-prd
awssu: .venv
	@unset AWS_PROFILE \
	&& unset AWS_DEFAULT_PROFILE \
	&& .venv/bin/awssu -i $(PROFILE)

## Installs a virtual environment and all python dependencies
.venv:
	virtualenv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -r requirements.txt --ignore-installed
	virtualenv --relocatable .venv

## Clean up
clean:
	rm -rf .venv
```

And example `requirements.txt`

```
ansible==2.2.0.0
ansible-lint==3.4.10
-e git+git@github.com:voytek-solutions/awssu.git#egg=awssu
```

With the following 2 files added to your project you can now simply run
`make awssu PROFILE=my-profile`. Now for 1h you can use your aws `my-profile`.
