import os
from optparse import make_option
from boto.s3.connection import S3Connection

from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Insert non-profit-organization default data"

    option_list = BaseCommand.option_list + (
        make_option('--reset-nav',
            action="store_true", dest='reset_nav', default=False,
            help='Reset the navigation'),
        make_option('--skip-media',
            action="store_true", dest='skip_media', default=False,
            help='Skip downloading media files'),
    )

    def handle(self, **options):
        """
        Load data and from non profit fixtures
        and download images from s3 location.
        """
        reset_nav = options.get('reset_nav', None)
        skip_media = options.get('skip_media', None)

        if not skip_media:
            self.copy_files()

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

    def copy_to_local(self):
        """
        Copy media files to a local directory.
        """
        conn = S3Connection(anon=True)
        bucket = conn.get_bucket('tendenci-static')
        bucket_list = bucket.list('npo_defaults')

        for source_key in bucket_list:
            if not source_key.name.endswith('/'):  # if file

                dst = source_key.name.replace('npo_defaults/', '')
                dst = os.path.join(settings.MEDIA_ROOT, dst)

                basename = os.path.basename(dst)
                dir_path = dst.replace(basename, '')

                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                print dst
                with open(dst, 'wb') as f:
                    f.write(source_key.read())

    def copy_to_s3(self):
        """
        Copy media files to this sites' S3 location.
        """
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket('tendenci-static')
        bucket_list = bucket.list('npo_defaults')

        for source_key in bucket_list:
            if not source_key.name.endswith('/'):  # if file

                target_key_name = source_key.name.replace('npo_defaults/', '')
                target_key_name = os.path.join(settings.MEDIA_ROOT, target_key_name)

                # TODO: Check if exists before copying over
                print settings.AWS_STORAGE_BUCKET_NAME, target_key_name
                source_key.copy(settings.AWS_STORAGE_BUCKET_NAME, target_key_name)

    def call_loaddata(self, reset_nav=False):
        """
        This calls the loaddata command on all
        non profit fixtures.
        The order - It's a big deal.
        """
        from tendenci.core.files.models import File

        if reset_nav:
            from tendenci.apps.navs.models import Nav
            try:
                main_nav = Nav.objects.get(pk=1)
                main_nav.delete()
            except:
                pass

        staff_installed = "addons.staff" in settings.INSTALLED_APPS
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
        if staff_installed:
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
            if 'staff' in unicode(f.file) and staff_installed:
                f.content_type = staff_ct

            f.save()

        suffix_list = [
            'profiles_profile',
            'events',
            'jobs',
            'memberships',
            'memberships_membershipdefault',
            'directories',
            'articles',
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
            filename = 'npo_default_%s.json' % suffix

            print filename
            call_command('loaddata', filename)

        call_command('set_theme', 'twenty-thirteen')
