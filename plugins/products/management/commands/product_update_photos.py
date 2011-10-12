from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Loop through all images in a directory.
        Associate the images to their product instance
        """
        import os
        import re
        import shutil
        import logging
        from django.conf import settings
        from django.db import connection, transaction
        from products.models import Product, ProductFile

        product_file = ProductFile()

        # declare logger
        logger = logging.getLogger('image_log')

        # declare handler
        handler = logging.FileHandler(os.path.join(
            settings.PROJECT_ROOT, 'plugins', 'products', 'management','commands','product_update_photos_error.log'))

        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)

        # 0 no output; 1 normal; 2 verbose; 3 very verbose
        verbosity = options['verbosity'] 

        cursor = connection.cursor()
        root_dir = os.path.join(settings.PROJECT_ROOT,'plugins','products','site_media','media','uploads','catalogs')

        print 'root_dir', root_dir

        # loop through directories
        for root, dirs, file_names in os.walk(root_dir):

            print 'root', root
            print 'dirs', dirs
            print 'file_names', file_names

            # directory name must be digit
            base_name = os.path.basename(root)
            if not base_name.isdigit():
                continue # on to the next one

            # match photo with product ----------------
            t4_pk = int(base_name)
            cursor.execute("SELECT t5_id FROM mig_product_t4_to_t5 WHERE t4_id = %s", [t4_pk])
            row = cursor.fetchone()

            if not row:
                logger.error('Product not found in south_migraiton table (T4 id: %s)' % t4_pk)
                continue  # on to the next one
            # -----------------------------------------

            try:  # get instance; use directory name
                instance = Product.objects.get(pk=row[0])
            except Product.DoesNotExist as e:
                logger.error('Product (T5 id: %s) not found in T5 table (T4 id: %s)' % (row[0], t4_pk))
                continue  # on to the next one

            if verbosity > 0:
                print instance, file_names

            # get list of file paths
            file_paths = [os.path.join(root_dir, base_name, file_name) for file_name in file_names]

            # get path to original file (largest file)
            file_path = ''
            file_size = 0
            for f in file_paths:
                if os.path.getsize(f) > file_size:
                    file_size = os.path.getsize(f)
                    file_path = f            

            # # copy files to directory
            # dst = os.path.join(settings.MEDIA_ROOT,'files','product', os.path.basename(file_path))
            # shutil.copy2(src, dst)  # copy2; metadata is copied as well

            file_object = ''

            if file_path:
                file_object = open(file_path)
                print 'file object', file_object.name
                file_object.close()

            # product_file.bind_files_to_instance(
            #     files = [file_object],
            #     instance = instance,
            # )