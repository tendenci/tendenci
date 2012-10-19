from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Set the media files permissions on S3.

    Example:
        ./manage.py set_media_files_perms
    """

    def handle(self, *apps, **kwargs):
        from tendenci.core.files.models import File as tFile
        from tendenci.libs.boto_s3.utils import set_s3_file_permission

        files = tFile.objects.all()
        count = 0
        for tfile in files:
            if tfile.file:
                if tfile.allow_anonymous_view:
                    perm = 'public'
                else:
                    perm = 'private'

                print 'Setting %s to %s' % (tfile.file.name,
                                            perm)

                set_s3_file_permission(tfile.file.name,
                                       public=(perm == 'public'))
                count += 1

        print 'Done'
        print 'Total files processed', count
