#!/usr/bin/env python

from __future__ import with_statement
from optparse import OptionParser
import os
from shutil import copy

from django.utils.importlib import import_module


def update_project():
    """
    Copies some of the project_template directory files into the
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
        files_to_copy = [
            os.path.join("conf", "__init__.py"),
            os.path.join("conf", "settings.py"),
            os.path.join("conf", "urls.py"),
            os.path.join("conf", "wsgi.py"),
            "deploy.py",
        ]
        for file_path in files_to_copy:
            copy(os.path.join(package_path, "project_template", file_path),
                 os.path.join(project_path, file_path))

    for (root, dirs, files) in os.walk(os.path.join(project_path, 'conf'), False):
        for f in files:
            if f.endswith(".pyc"):
                os.remove(os.path.join(root, f))

if __name__ == "__main__":
    update_project()
