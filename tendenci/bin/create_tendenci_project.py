#!/usr/bin/env python

from __future__ import with_statement
from distutils.dir_util import copy_tree
from optparse import OptionParser
import os
from shutil import move
from uuid import uuid4

from django.utils.importlib import import_module


def create_project():
    """
    Copies the contents of the project_template directory to the
    current directory.

    The logic for this type of project build out came from Mezzanine
    https://github.com/stephenmcd/mezzanine/blob/master/mezzanine/bin/mezzanine_project.py
    """
    parser = OptionParser(usage="usage: %prog")
    project_path = os.path.join(os.getcwd())

    # Create the list of packages to build from - at this stage it
    # should only be one or two names, tendenci plus an alternate
    # package.
    packages = ["tendenci"]
    for package_name in packages:
        try:
            __import__(package_name)
        except ImportError:
            parser.error("Could not import package '%s'" % package_name)

    # Build the project up copying over the project_template from
    # each of the packages.
    for package_name in packages:
        package_path = os.path.dirname(os.path.abspath(import_module(package_name).__file__))
        copy_tree(os.path.join(package_path, "project_template"), project_path)
        move(os.path.join(project_path, ".env_example"),
             os.path.join(project_path, ".env"))

    # Update the local environment file with custom KEYs
    env_path = os.path.join(os.getcwd(), ".env")

    # Generate a unique SECREY_KEY for the project's setttings module.
    with open(env_path, "r") as f:
        data = f.read()
    with open(env_path, "w") as f:
        secret_key = "%s%s" % (uuid4(), uuid4())
        f.write(data.replace("your_unique_secret_key", secret_key))

    # Generate a unique SITE_SETTINGS_KEY for the project's setttings module.
    with open(env_path, "r") as f:
        data = f.read()
    with open(env_path, "w") as f:
        setting_key = "%s%s" % (uuid4(), uuid4())
        f.write(data.replace("your_tendenci_sites_settings_key", setting_key[:32]))

    # Clean up pyc files.
    for (root, dirs, files) in os.walk(project_path, False):
        for f in files:
            if f.endswith(".pyc"):
                os.remove(os.path.join(root, f))

if __name__ == "__main__":
    create_project()
