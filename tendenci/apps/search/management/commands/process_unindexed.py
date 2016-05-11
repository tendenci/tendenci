#process_unindexed.py
from datetime import datetime

from django.core.management.base import BaseCommand
from django.core.management import call_command




class Command(BaseCommand):
    """
    Command used to process unindexed items by querying per Model
    and running update_index based on a calculated age
    for models with unindexed items.
    """

    def handle(self, **options):
        from tendenci.apps.search.models import UnindexedItem
        items = []
        ages = []

        unindexed_items = UnindexedItem.objects.all().select_related('content_type__app_label').order_by('create_dt')
        for ui in unindexed_items:
            app = ui.content_type.app_label
            if app not in items:
                items.append(app)

                age = datetime.now() - unindexed_items[0].create_dt
                age = (int(age.days)*60*60*24) + age.seconds
                age = (age / 3600) + 1
                ages.append(int(age))

        # If we have items, then we find the max age and run a single
        # update_index command for those apps with the longest age.
        if items and ages:
            ages.sort()
            ages.reverse()
            max_age = ages[0]
            # Remove is required because soft-deletes cannot be updated
            # in the index as the index cannot query for them to update
            # them.
            params = {'age': max_age, 'batch-size': 25, 'remove': True}

            call_command('update_index', *items, **params)
            unindexed_items.delete()
