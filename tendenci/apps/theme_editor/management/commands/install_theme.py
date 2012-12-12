import os
import zipfile
import urllib
from shutil import rmtree, move

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    """
    Example: python manage.py install_theme prfirm [theme_url]
    """

    def handle(self, theme_name, theme_url=None, **options):
        """
        Downloads a theme to be installed on the site and sets
        it as the active theme.
        """

        if not theme_url:
            theme_url = "https://github.com/tendenci/tendenci-themes/archive/master.zip"

        themes_dir_path = os.path.join(settings.PROJECT_ROOT, "themes")
        theme_path = os.path.join(themes_dir_path, theme_name)

        # Check if the theme already exists
        if os.path.isdir(theme_path):
            raise CommandError('The theme %s is already installed.' % theme_name)

        # Copy the theme files down
        theme_download = urllib.urlopen(theme_url)
        theme_zip_path = os.path.join(themes_dir_path, "%s.zip" % theme_name)
        theme_zip = open(theme_zip_path, 'wb')
        theme_zip.write(theme_download.read())
        theme_zip.close()

        # Unzip the theme files
        theme_zip_file = open(theme_zip_path, 'r')
        zfobj = zipfile.ZipFile(theme_zip_file)
        unzip_dirname = theme_name
        for i, name in enumerate(zfobj.namelist()):
            if i == 0:
                unzip_dirname = name[:-1]
            if name.endswith('/'):
                try:  # Don't try to create a directory if exists
                    os.mkdir(os.path.join(themes_dir_path, name))
                except:
                    pass
            else:
                outfile = open(os.path.join(themes_dir_path, name), 'wb')
                outfile.write(zfobj.read(name))
                outfile.close()

        # Delete the zip file
        os.remove(theme_zip_path)

        # Move the theme out of the unzipped folder
        move(os.path.join(themes_dir_path, unzip_dirname, theme_name), os.path.join(themes_dir_path, theme_name))

        rmtree(os.path.join(themes_dir_path, unzip_dirname))
