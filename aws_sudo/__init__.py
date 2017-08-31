#!/usr/bin/env python
#
# Syntax: aws-sudo [-i] [-e] [-m MFA-token] [-s 3600] <aws_profile_name> \
#             [<command> <command arg>*]
#

from __future__ import print_function

import argparse
import boto3
import botocore
import os
import sys
import aws_sudo.CommandParser
from six.moves import configparser


def sudo(cmd_args):
    profile_config = read_config(cmd_args.profile)
    credentials = {}

    profile_config['session_timeout'] = cmd_args.session_timeout
    profile_config['mfa_code'] = cmd_args.mfa_code
    credentials = get_credentials(profile_config)

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

    # save profile name for future use
    profiles[profile]['profile_name'] = profile

    return profiles[profile]


def print_exports(credentials):
    # Set AWS/Boto environemnt variables before executing target command
    print('export', end=' ')
    print('AWS_ACCESS_KEY_ID=' + (credentials['AccessKeyId']), end=' ')
    print('AWS_SECRET_ACCESS_KEY=' + (credentials['SecretAccessKey']), end=' ')
    print('AWS_SESSION_TOKEN=' + (credentials['SessionToken']), end=' ')
    print('AWS_SECURITY_TOKEN=' + (credentials['SessionToken']), end='')


def update_credentials(profile, credentials):
    credentials_file = os.path.expanduser('~/.aws/credentials')
    config = configparser.ConfigParser()
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


def get_credentials(profile_config):
    if 'role_arn' in profile_config:
        # Assume role with or without MFA token
        session = get_session(profile_config)
        return assume_role(session, profile_config)
    elif 'mfa_serial' in profile_config:
        # This is normal AMI with MFA token
        session = get_session(profile_config)
        return login_with_mfa(session, profile_config)
    elif 'source_profile' in profile_config or\
            'aws_access_key_id' not in profile_config:
        # This is most likely EC2 instance role
        session = get_session(profile_config)
        credentials = session.get_credentials().get_frozen_credentials()
        return {
            'AccessKeyId': credentials.access_key,
            'SecretAccessKey': credentials.secret_key,
            'SessionToken': str(credentials.token)
        }
    else:
        return {
            'AccessKeyId': profile_config['aws_access_key_id'],
            'SecretAccessKey': profile_config['aws_secret_access_key'],
            'SessionToken': ''
        }


def get_session(profile_config):
    session_profile = profile_config['profile_name']

    if 'source_profile' in profile_config:
        session_profile = profile_config['source_profile']

    if 'region' in profile_config:
        os.putenv('AWS_DEFAULT_REGION', profile_config['region'])
        os.putenv('AWS_REGION', profile_config['region'])

    # Create a session using profile or EC2 Instance Role
    # To use Instance Role set `source_profile` to empty string in aws profile
    # configuration file
    session = boto3.Session(profile_name=session_profile)

    return session


def login_with_mfa(session, profile_config):
    # Assume role using STS client
    sts_client = session.client('sts')
    credentials = sts_client.get_session_token(
        DurationSeconds=profile_config['session_timeout'],
        SerialNumber=profile_config['mfa_serial'],
        TokenCode=profile_config['mfa_code']
    )

    return credentials['Credentials']


def assume_role(session, profile_config):
    role_arn = profile_config['role_arn']

    # Assume role using STS client
    sts_client = session.client('sts')
    if 'mfa_serial' in profile_config:
        if profile_config['mfa_code'] is None:
            profile_config['mfa_code'] = raw_input("Enter MFA token: ")

        assumedRoleObject = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="AssumeRoleSession",
            DurationSeconds=profile_config['session_timeout'],
            SerialNumber=profile_config['mfa_serial'],
            TokenCode=profile_config['mfa_code']
        )
    else:
        assumedRoleObject = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="AssumeRoleSession",
            DurationSeconds=profile_config['session_timeout']
        )

    return assumedRoleObject['Credentials']


def main():
    sudo(CommandParser.CommandParser().get_arguments())
