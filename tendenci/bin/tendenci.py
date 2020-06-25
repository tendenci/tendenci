#!/usr/bin/env python
import fileinput
import fnmatch
import os
import re
import sys
from argparse import ArgumentParser
from difflib import unified_diff

from django.core.management import ManagementUtility


CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 6)

if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write("This version of Tendenci requires Python {}.{} or above - you are running {}.{}\n".format(*(REQUIRED_PYTHON + CURRENT_PYTHON)))
    sys.exit(1)


def pluralize(value, arg='s'):
    return '' if value == 1 else arg


class Command:
    description = None

    def create_parser(self, command_name=None):
        if command_name is None:
            prog = None
        else:
            # hack the prog name as reported to ArgumentParser to include the command
            prog = "%s %s" % (prog_name(), command_name)

        parser = ArgumentParser(
            description=getattr(self, 'description', None), add_help=False, prog=prog
        )
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser):
        pass

    def print_help(self, command_name):
        parser = self.create_parser(command_name=command_name)
        parser.print_help()

    def execute(self, argv):
        parser = self.create_parser()
        options = parser.parse_args(sys.argv[2:])
        options_dict = vars(options)
        self.run(**options_dict)


class CreateProject(Command):
    description = "Creates the directory structure for a new Tendenci project."

    def add_arguments(self, parser):
        parser.add_argument('project_name', help="Name for your Tendenci project")
        parser.add_argument('dest_dir', nargs='?', help="Destination directory inside which to create the project")

    def run(self, project_name=None, dest_dir=None):
        # Make sure given name is not already in use by another python package/module.
        try:
            __import__(project_name)
        except ImportError:
            pass
        else:
            sys.exit("'%s' conflicts with the name of an existing "
                     "Python module and cannot be used as a project "
                     "name. Please try another name." % project_name)

        print("Creating a Tendenci project called %(project_name)s" % {'project_name': project_name})  # noqa

        # First find the path to Tendenci
        template_path = "https://github.com/tendenci/tendenci-project-template/archive/master.zip"

        # Call django-admin startproject
        utility_args = ['django-admin.py',
                        'startproject',
                        '--template=' + template_path,
                        project_name]

        #if dest_dir:
            #utility_args.append(dest_dir)

        utility = ManagementUtility(utility_args)
        utility.execute()

        print("Success! %(project_name)s has been created" % {'project_name': project_name})  # noqa


COMMANDS = {
    'startproject': CreateProject(),
}


def prog_name():
    return os.path.basename(sys.argv[0])


def help_index():
    print("Type '%s help <subcommand>' for help on a specific subcommand.\n" % prog_name())  # NOQA
    print("Available subcommands:\n")  # NOQA
    for name, cmd in sorted(COMMANDS.items()):
        print("    %s%s" % (name.ljust(20), cmd.description))  # NOQA


def unknown_command(command):
    print("Unknown command: '%s'" % command)  # NOQA
    print("Type '%s help' for usage." % prog_name())  # NOQA
    sys.exit(1)


def main():
    try:
        command_name = sys.argv[1]
    except IndexError:
        help_index()
        return

    if command_name == 'help':
        try:
            help_command_name = sys.argv[2]
        except IndexError:
            help_index()
            return

        try:
            command = COMMANDS[help_command_name]
        except KeyError:
            unknown_command(help_command_name)
            return

        command.print_help(help_command_name)
        return

    try:
        command = COMMANDS[command_name]
    except KeyError:
        unknown_command(command_name)
        return

    command.execute(sys.argv)


if __name__ == "__main__":
    main()
