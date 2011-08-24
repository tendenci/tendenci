from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Loop through all images in a directory.
        Associate the images to the before_after application
        via the Files application.
        """
        import os
        from django.db import connection, transaction
        from django.conf import settings
        from files.models import File
        from before_and_after.models import BeforeAndAfter
        cursor = connection.cursor()

        root_dir = os.path.join(settings.MEDIA_ROOT,'uploads','image-crops')

        # loop through directories
        for root, dirs, file_names in os.walk(root_dir):
            t4_pk = int(os.path.basename(root))
            cursor.execute("SELECT t5_id FROM mig_before_after_t4_to_t5 WHERE t4_id = %s", [t4_pk])
            row = cursor.fetchone()


            try:  # get instance; use directory name
                instance = BeforeAndAfter.objects.get(pk=row['t5_id'])
            except BeforeAndAfter.DoesNotExist as e:
                continue  # on to the next one

            # get list of file paths
            file_paths = [os.path.join(root_dir, file_name) for f in file_names]

            files = []  # make file objects
            for file_path in file_paths:
                f = open(file_path)
                files.append(f)

            # associate files with instance (before_after innstance)
            files = File.objects.bind_files_to_instance(files, instance)

            # output
            print instance, files

            # close files
            for f in files: f.close()