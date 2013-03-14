from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """"
    Populate the blank entity and auth group fields for the user groups.
    For the blank entity field, fill out with the default entity (id=1).
    For the blank auth group field, get or create one by name if not exists.

    Usage: ./manage.py populate_entity_and_auth_group_columns
    """

    def handle(self, *args, **options):
        from tendenci.apps.entities.models import Entity
        from tendenci.apps.user_groups.models import Group

        groups = Group.objects.all()
        if groups:
            first_entity = Entity.objects.first()
            for ugroup in groups:
                if not ugroup.entity:
                    ugroup.entity = first_entity
                    ugroup.save()
                if not ugroup.group:
                    # the save method will take care of the auth group.
                    ugroup.save()