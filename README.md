# AWS SU

[![PyPI version](https://badge.fury.io/py/aws-sudo.svg)](https://badge.fury.io/py/aws-sudo)
[![Travis Status](https://travis-ci.org/voytek-solutions/aws-sudo.svg?branch=master)](https://travis-ci.org/voytek-solutions/aws-sudo)

Help with exporting AWS secrets and tokens when using assumed roles.

```
usage: aws-sudo [-h] [-i] [-e] [-m MFA_CODE] [-s SESSION_TIMEOUT]
                profile [command] [command_args]

positional arguments:
  profile               Name of the AWS profile
  command               Command to be executed
  command_args          Command arguments

optional arguments:
  -h, --help            show this help message and exit
  -i, --in-place        Should we udpate ~/.aws/credentials with tmp
                        credentials
  -e, --export          Should we output `unset` and `export` commands
  -m MFA_CODE, --mfa-code MFA_CODE
                        Your MFA code
  -s SESSION_TIMEOUT, --session-timeout SESSION_TIMEOUT
                        STS session timeout in seconds in the range 900..3600
```

The `--in-place` or `--export` option is useful if you want to de-couple running
build/deploy CI/CD tasks from granting IAM permissions.




## Examples

```
aws-sudo my-profile ansible-playbook ...

# unset & export
$(aws-sudo my-profile)
# ... with MFA
$(aws-sudo -m 135797 my-profile)

# MFA no interaction
aws-sudo -m 123789 my-profile ansible-playbook ...

# short lived session
aws-sudo -s 60 my-profile ansible-playbook ...

# update ~/.aws/credentials with tmp keys, secrets and tokens
aws-sudo -i my-profile

# create aws env file
aws-sudo my-profile > .aws-env
source .aws-env
```




## Contributors

This project was originally started by [leepa](https://github.com/leepa).

Other people involved (in alphabetical order):

* Kuehn Hagen
* Minton Chris
* Reed David
* Roche Christian
