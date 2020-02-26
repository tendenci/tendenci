
import os.path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    """
    If static files are served on an external server, such as AWS S3,
    the hard-coded /static/ url in the static files (css, js) needs
    to be replaced with the absolute url to the external source.

    Usage: manage.py s3_replace_static_urls
    """

    def handle(self, *args, **options):
        import mimetypes
        import boto
        from boto.s3.key import Key

        if all([settings.AWS_ACCESS_KEY_ID,
                settings.AWS_SECRET_ACCESS_KEY,
                settings.AWS_STORAGE_BUCKET_NAME,
                settings.AWS_LOCATION]):
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            bucket_site_folder_name = settings.AWS_LOCATION

            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                                   settings.AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(bucket_name)
            k = Key(bucket)

            theme_root = settings.ORIGINAL_THEMES_DIR
            if os.path.isdir(theme_root):
                for dirpath, dirnames, filenames in os.walk(theme_root):
                    for filename in filenames:
                        file_path = (os.path.join(dirpath, filename)
                                    ).replace('\\', '/')
                        key = '%s/%s/%s' % (bucket_site_folder_name,
                                        dirpath.replace(theme_root, 'themes'),
                                        filename)
                        k.key = key
                        if os.path.splitext(filename)[1] == '.less':
                            content_type = 'text/css'
                        else:
                            content_type = mimetypes.guess_type(filename)[0] or k.DefaultContentType
                        k.set_metadata('Content-Type', content_type)

                        k.set_contents_from_filename(file_path, replace=True)
                        # keep html files private
                        if os.path.splitext(filename)[1] not in ['.html']:
                            k.set_acl('public-read')
                        print(key)
