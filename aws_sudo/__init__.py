#!/usr/bin/env python
#
# Syntax: aws-sudo [-i] [-e] [-m MFA-token] [-s 3600] <aws_profile_name> \
#             [<command> <command arg>*]
#

import argparse
import boto3
import botocore
import os
import sys
import CommandParser

# For python 2.7 and 3 support
try:
    from configparser import configparser
except ImportError:
    from ConfigParser import ConfigParser as configparser


def sudo(cmd_args):
    config = read_config(cmd_args.profile)
    credentials = assume_role(config, cmd_args.session_timeout, cmd_args.mfa_code)

    if cmd_args.mode is 'in_place':
        update_credentials(cmd_args.profile, credentials)
    elif cmd_args.mode is 'export':
        print_exports(credentials)
    elif cmd_args.mode is 'proxy':
        proxy_command(cmd_args.command, cmd_args.command_args, credentials)


def read_config(profile):
    """This reads our config files automatically, and combines config and
    credentials files for us"""
    profiles = botocore.session.get_session().full_config.get('profiles', {})

    # Checks for the passed in profile, mostly for sanity
    if profile not in profiles:
        print("Profile '%s' does not exist in the config file." % profile)
        quit(2)

    if (
        'role_arn' not in profiles[profile] or
        'source_profile' not in profiles[profile]
    ):
        print(
            "Profile '%s' does not have role_arn "
            "or source_profile set." % profile
        )
        quit(3)

    return profiles[profile]


def print_exports(credentials):
    # Unset variables for sanity sake
    # print("unset AWS_DEFAULT_PROFILE AWS_PROFILE AWS_ACCESS_KEY_ID \
    #     AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_SECURITY_TOKEN\n\n")

    # Set AWS/Boto environemnt variables before executing target command
    print('export ')
    print('AWS_ACCESS_KEY_ID=' + (credentials['AccessKeyId']))
    print('AWS_SECRET_ACCESS_KEY=' + (credentials['SecretAccessKey']))
    print('AWS_SESSION_TOKEN=' + (credentials['SessionToken']))
    print('AWS_SECURITY_TOKEN=' + (credentials['SessionToken']))


def update_credentials(profile, credentials):
    credentials_file = os.path.expanduser('~/.aws/credentials')
    config = configparser()
    config.read(credentials_file)

    # Create profile section in credentials file
    if not config.has_section(profile):
        config.add_section(profile)

    # Set access credentials
    # `aws_security_token` is used by boto
    # `aws_session_token` is used by aws cli
    config.set(
        profile, 'aws_access_key_id', credentials['AccessKeyId'])
    config.set(
        profile, 'aws_secret_access_key', credentials['SecretAccessKey'])
    config.set(
        profile, 'aws_session_token', credentials['SessionToken'])
    config.set(
        profile, 'aws_security_token', credentials['SessionToken'])

    # Update credentials file
    with open(credentials_file, 'w') as credentials_file:
        config.write(credentials_file)

    print(
        "# Aws credentials file got updated with temporary access for profile %s"
        % profile
    )


def proxy_command(command, command_args, credentials):
    # Unset variables for sanity sake
    os.unsetenv('AWS_DEFAULT_PROFILE')
    os.unsetenv('AWS_PROFILE')
    os.unsetenv('AWS_ACCESS_KEY_ID')
    os.unsetenv('AWS_SECRET_ACCESS_KEY')
    os.unsetenv('AWS_SESSION_TOKEN')
    os.unsetenv('AWS_SECURITY_TOKEN')

    # Set AWS/Boto environemnt variables before executing target command
    os.putenv('AWS_ACCESS_KEY_ID', (credentials['AccessKeyId']))
    os.putenv('AWS_SECRET_ACCESS_KEY', (credentials['SecretAccessKey']))
    os.putenv('AWS_SESSION_TOKEN', (credentials['SessionToken']))
    os.putenv('AWS_SECURITY_TOKEN', (credentials['SessionToken']))

    command_status = os.system(command + " " + " ".join(command_args))
    exit(os.WEXITSTATUS(command_status))


def assume_role(config, session_timeout, mfa_code=None):
    role_arn = config['role_arn']

    if 'region' in config:
        os.putenv('AWS_DEFAULT_REGION', config['region'])
        os.putenv('AWS_REGION', config['region'])

    # Create a session using profile or EC2 Instance Role
    # To use Instance Role set `source_profile` to empty string in aws profile
    # configuration file
    session = boto3.Session(profile_name=(config['source_profile'] or None))

    # Assume role using STS client
    sts_client = session.client('sts')
    if 'mfa_serial' in config:
        if mfa_code is None:
            mfa_code = raw_input("Enter MFA token: ")

        assumedRoleObject = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="AssumeRoleSession",
            DurationSeconds=session_timeout,
            SerialNumber=config['mfa_serial'],
            TokenCode=mfa_code
        )
    else:
        assumedRoleObject = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="AssumeRoleSession",
            DurationSeconds=session_timeout
        )

    # print(
    #     "# Assumed '%s' role using '%s' profile. Expiration Token: %s"
    #     % (
    #         role_arn,
    #         config['source_profile'],
    #         str(assumedRoleObject['Credentials']['Expiration'])
    #     )
    # )

    return assumedRoleObject['Credentials']


def main():
    sudo(CommandParser.CommandParser().get_arguments())
