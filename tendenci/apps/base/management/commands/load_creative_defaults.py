from __future__ import print_function
import os
from optparse import make_option
from random import randint
from boto.s3.connection import S3Connection

from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Insert default data"

    option_list = BaseCommand.option_list + (
        make_option('--reset-nav',
            action="store_true", dest='reset_nav', default=False,
            help='Reset the navigation'),
    )

    def handle(self, **options):
        """
        Load data and from non profit fixtures
        and download images from s3 location.
        """
        reset_nav = options.get('reset_nav', None)
        self.number_used = []

        self.call_loaddata(reset_nav)

    def copy_files(self):
        """
        Copy files from default S3 location
        into websites S3 or local directory.
        """
        if settings.USE_S3_STORAGE:
            self.copy_to_s3()
        else:
            self.copy_to_local()

    def call_loaddata(self, reset_nav=False):
        """
        This calls the loaddata command on all creative fixtures.
        """
        from tendenci.apps.files.models import File

        if reset_nav:
            from tendenci.apps.navs.models import NavItem
            try:
                main_nav_items = NavItem.objects.filter(nav_id=1)
                main_nav_items.delete()
            except:
                pass

        print('creative_default_auth_user.json')
        call_command('loaddata', 'creative_default_auth_user.json')
        print('creative_default_auth_groups.json')
        call_command('loaddata', 'creative_default_auth_groups.json')
        print('creative_default_entities.json')
        call_command('loaddata', 'creative_default_entities.json')
        print('creative_default_user_groups.json')
        call_command('loaddata', 'creative_default_user_groups.json')
        print('creative_default_files.json')
        call_command('loaddata', 'creative_default_files.json')
        print('load creative_default_paymentmethod.json')
        call_command('loaddata', 'creative_default_paymentmethod.json')
        print('load creative_default_forums.json')
        call_command('loaddata', 'creative_default_forums.json')
        print('load creative_default_regions_region.json')
        call_command('loaddata', 'creative_default_regions_region.json')
        print('load creative_default_directories_pricings.json')
        call_command('loaddata', 'creative_default_directories_pricings.json')


        suffix_list = [
            'profiles_profile',
            'explorer',
            'events',
            'jobs',
            'memberships',
            'corporate_memberships',
            'articles',
            'forms',
            'forums',
            'news',
            'photos',
            'boxes',
            'pages',
            'navs',
            'stories',
            'videos',
        ]   

        # call loaddata on fixtures
        for suffix in suffix_list:
            filename = 'creative_default_%s.json' % suffix

            print(filename)
            call_command('loaddata', filename)

