import os
import zipfile
import urllib
from shutil import rmtree, move
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    """
    Example: python manage.py install_theme prfirm [theme_url]
    """

    option_list = BaseCommand.option_list + (
        make_option(
            '--all', action='store_true',
            dest='all', default=False,
            help='Install all themes'),
    )

    def handle(self, theme_name=None, theme_url=None, **options):
        """
        Downloads a theme to be installed on the site and sets
        it as the active theme.
        """
        from tendenci.apps.base.models import UpdateTracker

        UpdateTracker.start()
        all_themes = options.get('all', False)

        if not theme_url:
            theme_url = "https://github.com/tendenci/tendenci-project-template/archive/master.zip"

        if not (theme_name or all_themes):
            raise CommandError('Specify a theme name, or add --all for all themes')

        themes_dir_path = os.path.join(settings.PROJECT_ROOT, "themes")
        if theme_name:
            theme_path = os.path.join(themes_dir_path, theme_name)

            # Check if the theme already exists
            if os.path.isdir(theme_path):
                raise CommandError('The theme %s is already installed.' % theme_name)

        # Copy the theme files down
        theme_download = urllib.urlopen(theme_url)
        theme_zip_path = os.path.join(themes_dir_path, "themes.zip")
        theme_zip = open(theme_zip_path, 'wb')
        theme_zip.write(theme_download.read())
        theme_zip.close()

        # Unzip the theme files
        theme_zip_file = open(theme_zip_path, 'r')
        zfobj = zipfile.ZipFile(theme_zip_file)
        unzip_dirname = "themes"
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

        # Move the themes out of the unzipped folder
        unzip_dir_path = os.path.join(themes_dir_path, os.path.join(unzip_dirname, 'themes'))
        if all_themes:
            for name in os.listdir(unzip_dir_path):
                # Check for themes
                if os.path.isdir(os.path.join(unzip_dir_path, name)) and not name.startswith('.'):
                    # Check if the theme already exists
                    if not os.path.isdir(os.path.join(themes_dir_path, name)):
                        move(os.path.join(unzip_dir_path, name), os.path.join(themes_dir_path, name))
        elif theme_name:
            move(os.path.join(unzip_dir_path, theme_name), os.path.join(themes_dir_path, theme_name))

        rmtree(os.path.join(themes_dir_path, unzip_dirname))
        UpdateTracker.end()
