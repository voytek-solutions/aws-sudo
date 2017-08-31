import argparse
import sys


class CommandParser:
    def __init__(self):
        self.parser = ArgumentParser(
           formatter_class=argparse.RawDescriptionHelpFormatter,
           epilog="""description:
'sudo' but with AWS profiles.
"""
        )
        self.setup_arguments(self.parser)

    def get_parser(self):
        return self.parser

    def get_arguments(self, args=None):
        arguments, _ = self.parser.parse_known_args(args)

        if arguments.mode is None:
            if arguments.command is None:
                arguments.mode = 'export'
            else:
                arguments.mode = 'proxy'

        return arguments

    def setup_arguments(self, parser):
        parser.add_argument(
            '-i', '--in-place',
            dest='mode',
            const='in_place',
            help='Should we udpate ~/.aws/credentials with tmp credentials',
            action='store_const'
        )

        parser.add_argument(
            '-e', '--export',
            dest='mode',
            const='export',
            help='Should we output `unset` and `export` commands',
            action='store_const'
        )

        parser.add_argument(
            '-m', '--mfa-code',
            dest='mfa_code',
            help='Your MFA code',
            type=str
        )

        parser.add_argument(
            '-s', '--session-timeout',
            dest='session_timeout',
            help='STS session timeout in seconds in the range 900..3600',
            type=int,
            default=3600
        )

        parser.add_argument(
            'profile',
            help='Name of the AWS profile',
            default=''
        )

        parser.add_argument(
            'command',
            help='Command to be executed',
            nargs='?'
        )

        parser.add_argument(
            'command_args',
            nargs=argparse.REMAINDER,
            help='Command arguments',
        )


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()
        sys.stderr.write('error: %s\n' % message)
        sys.exit(2)
