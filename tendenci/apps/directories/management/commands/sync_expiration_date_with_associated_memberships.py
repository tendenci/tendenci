from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Snyc expiration date with their associated memberships or corporate memberships.

    Usage: python manage.py sync_expiration_date_with_associated_memberships
    """
    def handle(self, *args, **kwargs):
        from django.utils import timezone
        from tendenci.apps.directories.models import Directory
        
        now = timezone.now()
        for directory in Directory.objects.filter(status=True):
            if directory.is_associated_with_membership():
                if directory.expiration_dt:
                    new_expiration_dt = directory.get_expiration_dt()
                    if new_expiration_dt > now:
                        if directory.expiration_dt < new_expiration_dt:
                            print('Updating ', directory)
                            directory.expiration_dt = new_expiration_dt
                            if directory.status_detail == 'inactive':
                                directory.status_detail = 'active'
                            print(directory, ' ...updated')
                            directory.save(update_fields=['expiration_dt', 'status_detail'])
                        
                        