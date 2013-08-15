from django.core.management.base import BaseCommand
from django.db.models.loading import get_models


class Command(BaseCommand):
    """
    Delete soft deleted items.

    Loop through all models that are subclasses of the TendenciBaseModel
    and delete all soft deleted items.

    Usage:
        .manage.py delete_soft_deleted_items
    """
    def handle(self, *args, **options):
        from tendenci.core.perms.models import TendenciBaseModel
        models = get_models()
        for model in models:
            if TendenciBaseModel in model.__bases__:
                if hasattr(model.objects, 'all_inactive'):
                    items = model.objects.all_inactive()
                else:
                    items = model.objects.filter(status=False)
                for item in items:
                    #print 'Deleting ', item
                    item.hard_delete()
