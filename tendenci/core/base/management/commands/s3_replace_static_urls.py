import os

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
        import cStringIO
        import mimetypes
        import boto
        from boto.s3.key import Key

        if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            bucket_site_folder_name = settings.AWS_LOCATION
            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                                   settings.AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(bucket_name)
            k = Key(bucket)

            static_root = settings.STATIC_ROOT
            static_url_to_find = '/static/'
            static_url_replace_with = settings.STATIC_URL

            if os.path.isdir(static_root):
                # walk through the directory
                for dirpath, dirnames, filenames in os.walk(static_root):
                    for filename in filenames:
                        # skip the jquery and websymbols.css
                        if filename.find('jquery') == -1 and filename != 'websymbols.css':
                            if os.path.splitext(filename)[1] in ['.js', '.css', '.less']:
                                file_path = (os.path.join(dirpath, filename)
                                             ).replace('\\', '/')

                                with open(file_path) as f:
                                    content = f.read()
                                    if content.find(static_url_to_find) != -1:
                                        new_content = content.replace(
                                            static_url_to_find,
                                            static_url_replace_with)
                                        # upload to s3
                                        key = '%s/%s/%s' % (bucket_site_folder_name,
                                                            dirpath.replace(static_root, 'static'), filename)

                                        k.key = key

                                        content_type = mimetypes.guess_type(filename)[0] or k.DefaultContentType
                                        k.set_metadata('Content-Type', content_type)
                                        myfile = cStringIO.StringIO(new_content)
                                        k.set_contents_from_file(myfile, replace=True)
                                        myfile.close()
                                        #k.set_contents_from_string(new_content, replace=True)
                                        k.set_acl('public-read')
                                        print file_path

        else:
            print 'Site is not using S3 Storage.'
