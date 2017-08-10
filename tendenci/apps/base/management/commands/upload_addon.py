from __future__ import print_function
from optparse import make_option
import os
import zipfile

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Addon upload process.

    Usage:
        example:
        python manage.py upload_addon --zip_path /uploads/addons/addon.zip
    """

    option_list = BaseCommand.option_list + (
        make_option(
            '--zip_path',
            action='store',
            dest='zip_path',
            default='',
            help='Path to the zip file'),
    )

    def handle(self, *args, **options):
        path = options['zip_path']
        addon_zip = zipfile.ZipFile(default_storage.open(path))
        addon_name = addon_zip.namelist()[0]
        addon_name = addon_name.strip('/')

        addon_zip.extractall(settings.SITE_ADDONS_PATH)

        print("Updating tendenci site")
        os.system('python manage.py syncdb --noinput')
        os.system('python manage.py migrate %s --noinput' % addon_name)
        os.system('python manage.py update_settings %s' % addon_name)
        os.system('python manage.py collectstatic --noinput')

        print("Restarting Server")
        os.system('sudo reload %s' % os.path.basename(settings.PROJECT_ROOT))

        print('Deleting zip file')
        default_storage.delete(path)
