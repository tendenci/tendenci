import os
import mimetypes
import boto
from boto.s3.key import Key

from django.conf import settings


def save_file_to_s3(file_path, dirpath=None, public=False):
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
            
        key = '%s%s' % (settings.AWS_LOCATION,
                            file_path.replace(os.path.dirname(dirpath), ''))
        k.key = key
        if os.path.splitext(filename)[1] == '.less':
            content_type = 'text/css'
        else:
            content_type = mimetypes.guess_type(filename)[0] or k.DefaultContentType
        k.set_metadata('Content-Type', content_type) 
        k.set_contents_from_filename(file_path, replace=True)
        #print key
        
        if public:
            k.set_acl('public-read')
        