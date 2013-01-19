import os
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from boto.s3.connection import S3Connection


class Command(BaseCommand):
    help = "Insert non-profit-organization default data"

    def handle(self, **options):
        """
        Load data and from non profit fixtures
        and download images from s3 location.
        """
        self.copy_files()
        self.call_loaddata()

    def copy_files(self):
        """
        Copy files from default s3 location
        into websites s3 location.
        """
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)

        bucket = conn.get_bucket('tendenci-static')
        bucket_list = bucket.list('npo_defaults')

        for source_key in bucket_list:
            if not source_key.name.endswith('/'):  # if not directory

                target_key_name = source_key.name.replace('npo_defaults/', '')
                target_key_name = os.path.join(settings.MEDIA_ROOT, target_key_name)

                # TODO: Check if exists before copying over

                print settings.AWS_STORAGE_BUCKET_NAME, target_key_name
                source_key.copy(settings.AWS_STORAGE_BUCKET_NAME, target_key_name)

    def call_loaddata(self):
        """
        This calls the loaddata command on all
        non profit fixtures.
        The order - It's a big deal.
        """
        from tendenci.core.files.models import File

        print 'npo_default_auth_user.json'
        call_command('loaddata', 'npo_default_auth_user.json')
        print 'npo_default_entities.json'
        call_command('loaddata', 'npo_default_entities.json')
        print 'npo_default_user_groups.json'
        call_command('loaddata', 'npo_default_user_groups.json')
        print 'npo_default_files.json'
        call_command('loaddata', 'npo_default_files.json')

        box_ct = ContentType.objects.get(app_label='boxes', model='box')
        story_ct = ContentType.objects.get(app_label='stories', model='story')
        setting_ct = ContentType.objects.get(app_label='site_settings', model='setting')
        staff_ct = ContentType.objects.get(app_label='staff', model='staff')

        files = File.objects.all()

        print 'updating files'
        for f in files:

            if 'box' in unicode(f.file):
                f.content_type = box_ct
            if 'story' in unicode(f.file):
                f.content_type = story_ct
            if 'setting' in unicode(f.file):
                f.content_type = setting_ct
            if 'staff' in unicode(f.file):
                f.content_type = staff_ct

            f.save()

        suffix_list = [
            'profiles_profile'
            'events',
            'jobs',
            'memberships',
            'memberships_membershipdefault',
            'news',
            'photos',
            'boxes',
            'pages',
            'navs',
        ]

        # call loaddata on fixtures
        for suffix in suffix_list:
            filename = 'npo_default_%s.json' % suffix

            print filename
            call_command('loaddata', filename)

        call_command('loaddata', 'npo_default_stories.json')
