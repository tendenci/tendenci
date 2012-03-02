from datetime import datetime

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.contenttypes.models import ContentType

from registry import site as registry_site
from search.models import UnindexedItem

class Command(BaseCommand):
    """
    Command used to process unindexed items by querying per Model
    and running update_index based on a calculated age
    for models with unindexed items.
    """

    def handle(self, **options):
        registered_apps = registry_site.get_registered_apps()

        items = []
        ages = []
        ui_querysets = []

        for app in registered_apps:
            content_type = ContentType.objects.get_for_model(app['model'])
            unindexed_items = UnindexedItem.objects.filter(content_type=content_type).order_by('create_dt')
            if unindexed_items:
                age = datetime.now() - unindexed_items[0].create_dt
                age = (int(age.days)*60*60*24) + age.seconds
                age = (age / 3600) + 1

                ages.append(int(age))
                items.append(app['model']._meta.app_label)
                ui_querysets.append(unindexed_items)

                # Moved individual update_index commands out in favor
                # of combining all app updates into one command

                # params = {'age': age,}
                # items = [app['model']._meta.app_label]
                # call_command('update_index', *items, **params)
                # ui_querysets.delete()


        # If we have items, find the max age, and run 1 update_index command
        # with the longest age
        if items and ages:
            ages.sort()
            ages.reverse()
            max_age = ages[0]
            params = {'age': max_age, 'remove': True}

            call_command('update_index', *items, **params)

            for ui in ui_querysets:
                ui.delete()
