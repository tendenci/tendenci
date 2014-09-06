from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    For performance reason, clear all non-group perms from objectpermission.
    """
    def handle(self, *args, **options):
        from tendenci.apps.perms.object_perms import ObjectPermission

        ObjectPermission.objects.filter(group__isnull=True).delete()
