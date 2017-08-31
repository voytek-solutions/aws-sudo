import CommandParser
import unittest


class TestCommandParser(unittest.TestCase):
    def setUp(self):
        self.parser = CommandParser.CommandParser()

    # test default values
    def test_defaults(self):
        args = self.parser.get_arguments(
            'aws-sudo test-profile test-command'.split()[1:]
        )
        self.assertEqual(args.mfa_code, None)
        self.assertEqual(args.session_timeout, 3600)

    def test_export_mode_when_no_command(self):
        args = self.parser.get_arguments(
            'aws-sudo test-profile'.split()[1:]
        )
        self.assertEqual(args.mode, 'export')

    # test subcommand args names that clashes with aws-sudo args
    def test_duplicated_parameters(self):
        args = self.parser.get_arguments(
            'aws-sudo -m 123 test-profile test-command -m 321'.split()[1:]
        )
        self.assertEqual(args.mfa_code, '123')
        self.assertEqual(args.command_args, ['-m', '321'])

        args = self.parser.get_arguments(
            'aws-sudo -m 123 -s 3600 test-profile test-command -m 321 -s 10'
            .split()[1:]
        )
        self.assertEqual(args.mfa_code, '123')
        self.assertEqual(args.session_timeout, 3600)
        self.assertEqual(args.command_args, ['-m', '321', '-s', '10'])

    def test_in_place(self):
        args = self.parser.get_arguments(
            'aws-sudo -i -s 3600 test-profile test-command'.split()[1:]
        )
        self.assertEqual(args.mode, 'in_place')

        args = self.parser.get_arguments(
            'aws-sudo -i test-profile test-command -i'.split()[1:]
        )
        self.assertEqual(args.mode, 'in_place')

        args = self.parser.get_arguments(
            'aws-sudo -i test-profile'.split()[1:]
        )
        self.assertEqual(args.mode, 'in_place')

        args = self.parser.get_arguments(
            'aws-sudo test-profile test-command -i lorem'.split()[1:]
        )
        self.assertEqual(args.mode, 'proxy')

        args = self.parser.get_arguments(
            'aws-sudo test-profile test-command -i'.split()[1:]
        )
        self.assertEqual(args.mode, 'proxy')


if __name__ == '__main__':
    unittest.main()
