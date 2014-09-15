import os
from datetime import datetime
import mimetypes
import boto
from boto.s3.key import Key
from timezones.utils import adjust_datetime_to_timezone
from django.conf import settings
import dateutil.parser as dparser
from django.core.files.storage import default_storage
from storages.backends.s3boto import S3BotoStorage, S3BotoStorageFile


class StaticStorage(S3BotoStorage):
    """
    Storage for static files.
    The folder is defined in settings.STATIC_S3_PATH
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.STATIC_S3_PATH
        super(StaticStorage, self).__init__(*args, **kwargs)

    def url(self, name):
        url = super(StaticStorage, self).url(name)
        if name.endswith('/') and not url.endswith('/'):
            url += '/'
        return url


class DefaultStorage(S3BotoStorage):
    """
    Storage for uploaded media files.
    The folder is defined in settings.DEFAULT_S3_PATH
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.DEFAULT_S3_PATH
        super(DefaultStorage, self).__init__(*args, **kwargs)


def read_media_file_from_s3(file_path):
    """
    Read a media file from S3.
    The file_path should be the relative path in the media directory.

    Example:
    file_content = read_media_file_from_s3('/files/99/Earth-and-Moon.gif')
    """
    # the DEFAULT_S3_PATH is where the media files are stored.
    file_path = '%s/%s' % (settings.DEFAULT_S3_PATH, unicode(file_path).lstrip('/'))
    storage = S3BotoStorage()
    f = S3BotoStorageFile(file_path, 'r', storage)
    content = f.read()
    f.close()

    return content


def read_theme_file_from_s3(file_path):
    """
    Read a theme file from S3.
    The file_path should be the relative path in the media directory.

    Example:
    file_content = read_theme_file_from_s3('themename/templates/default.html')
    """
    # the DEFAULT_S3_PATH is where the media files are stored.
    file_path = '%s/%s' % (settings.THEME_S3_PATH, unicode(file_path).lstrip('/'))
    storage = S3BotoStorage()
    f = S3BotoStorageFile(file_path, 'r', storage)
    content = f.read()
    f.close()

    return content


def save_file_to_s3(file_path, dirpath=None, public=False, dest_path=None):
    """
    Save the file to S3.
    """
    if settings.USE_S3_STORAGE:
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                               settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        k = Key(bucket)

        filename = os.path.split(file_path)[1]

        if not dirpath:
            dirpath = settings.ORIGINAL_THEMES_DIR

        if not dest_path:
            dest_path = file_path.replace(os.path.dirname(dirpath), '')

        key = '%s%s' % (settings.AWS_LOCATION, dest_path)
        k.key = key
        if os.path.splitext(filename)[1] == '.less':
            content_type = 'text/css'
        else:
            content_type = mimetypes.guess_type(filename)[0] or k.DefaultContentType
        k.set_metadata('Content-Type', content_type)
        k.set_contents_from_filename(file_path, replace=True)

        if public:
            k.set_acl('public-read')


def set_s3_file_permission(file, public=False):
    """
    Save the file to S3.
    """
    if settings.USE_S3_STORAGE:
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                               settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        k = Key(bucket)

        file_path = unicode(file)

        k.key = '%s%s' % (settings.MEDIA_ROOT, file)

        if default_storage.exists(file_path):
            if public:
                k.set_acl('public-read')
            else:
                k.set_acl('private')
        else:
            print file_path, 'does not exist.'


def download_files_from_s3(prefix='', to_dir='', update_only=False, dry_run=False):
    """
    Retrieve the files inside the prefix (ex: themes) from S3,
    and store them to the directory to_dir.

    Example use:

    To download all files in the themes folder, call:

        download_files_from_s3(prefix='themes', to_dir='/path/to/site/themes')

    :type prefix: string
    :param prefix: The prefix of where to retrieve the files from s3

    :type to_dir: string
    :param to_dir: The directory of where to download the files

    :type update_only: bool
    :param update_only: If True, only update the modified files, otherwise,
                        overwrite the existing files.

    :type dry_run: bool
    :param dry_run: If True, do everything except saving the files.

    """
    if not prefix:
        print 'No prefix, exiting..'
        return
    if not os.path.isdir(to_dir):
        print 'Destination directory does not exist.'
        return

    if all([settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY,
            settings.AWS_STORAGE_BUCKET_NAME,
            settings.AWS_LOCATION]):
        name = '%s/%s' % (settings.AWS_LOCATION, prefix)
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                               settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

        for item in bucket.list(prefix=name):
            s3_file_relative_path = item.name.replace(name, '').lstrip('/')
            copy_to_fullpath = os.path.join(to_dir, s3_file_relative_path)
            copy_to_dir = os.path.dirname(copy_to_fullpath)
            if not os.path.isdir(copy_to_dir):
                # directory not exists, create it
                os.makedirs(copy_to_dir)

            if update_only and os.path.isfile(copy_to_fullpath):
                # check if this file from s3 has been modified.
                # if not modified, no need to update.
                src_modified_dt = dparser.parse(item.last_modified)
                dst_modified_dt = datetime.fromtimestamp(os.path.getmtime(copy_to_fullpath))
                # adjust the timezone for dst_modified_dt
                # to compare the modified date time in the same time zone
                dst_modified_dt = adjust_datetime_to_timezone(
                                            dst_modified_dt,
                                            from_tz=settings.TIME_ZONE,
                                            to_tz=src_modified_dt.tzname())
                if dst_modified_dt == src_modified_dt:
                    # source is current, no need to update
                    print 'Not modified %s' % s3_file_relative_path
                    continue

                elif dst_modified_dt > src_modified_dt:
                    print "Not updated. %s is current." % s3_file_relative_path
                    continue

            if dry_run:
                print 'Pretended to download %s' % s3_file_relative_path
            else:
                item.get_contents_to_filename(copy_to_fullpath)
                print 'Downloaded %s' % s3_file_relative_path

def delete_file_from_s3(file):
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                           settings.AWS_SECRET_ACCESS_KEY)
    b = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
    k = Key(b)
    k.key = file
    b.delete_key(k)
