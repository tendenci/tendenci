from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Loop through all images in a directory.
        Associate the images to their before_and_after instance
        """
        import os
        import shutil
        import logging
        from django.db import connection, transaction
        from django.conf import settings
        from django.core.files.uploadedfile import UploadedFile
        from files.models import File
        from before_and_after.models import BeforeAndAfter, PhotoSet

        logger = logging.getLogger('image_log')
        handler = logging.FileHandler(os.path.join(settings.PROJECT_ROOT, 'plugins', 'before_and_after', 'the.log'))
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)

        # 0 no output; 1 normal; 2 verbose; 3 very verbose
        verbosity = options['verbosity'] 

        cursor = connection.cursor()
        root_dir = os.path.join(settings.PROJECT_ROOT,'site_media','uploads','image-crops')

        # loop through directories
        for root, dirs, file_names in os.walk(root_dir):

            # directory name must be digit
            base_name = os.path.basename(root)
            if not base_name.isdigit():
                continue # on to the next one

            t4_pk = int(base_name)
            cursor.execute("SELECT t5_id FROM mig_before_after_t4_to_t5 WHERE t4_id = %s", [t4_pk])
            row = cursor.fetchone()

            try:  # get instance; use directory name
                if row: instance = BeforeAndAfter.objects.get(pk=row[0])
            except BeforeAndAfter.DoesNotExist as e:
                continue  # on to the next one

            if verbosity == 1:
                print instance, file_names

            # get list of file paths
            file_paths = [os.path.join(root_dir, base_name, file_name) for file_name in file_names]

            # copy files to directory
            for src in file_paths:
                dst = os.path.join(settings.MEDIA_ROOT,'files','before_and_after', os.path.basename(src))
                shutil.copy2(src, dst)  # copy2; metadata is copied as well

            # update instance records with photos
            for i in range(10):
                for file_name in file_names:
                    before_photo, after_photo = '', ''
                    temp_name = file_name.lower()
                    temp_name = os.path.splitext(temp_name)[0]
                    temp_name = temp_name.split('_')[-1:][0]

                    if len(temp_name) != 2:
                        logger.error('%s' % file_name)
                        continue  # on to the next one

                    order, half = temp_name

                    if not order.isdigit():
                        continue # on to the next one

                    rel_path = '/files/before_and_after/%s' % file_name

                    if half == 'a': after_photo = rel_path
                    elif half == 'b': before_photo= rel_path

                    try:
                        photo_set = PhotoSet.objects.get(
                            order=order,
                            before_and_after=instance,
                        )

                        if after_photo:
                            photo_set.after_photo = after_photo
                        elif before_photo:
                            photo_set.before_photo = before_photo

                        photo_set.save()

                    except PhotoSet.DoesNotExist as e:
                        photo_set = PhotoSet.objects.create(**{
                            'order': order,
                            'before_and_after': instance,
                            'before_photo': before_photo,
                            'after_photo': after_photo,
                        })