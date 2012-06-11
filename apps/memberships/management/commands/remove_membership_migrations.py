from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    This is a temporary command that will be removed soon.
    This command will remove specific migration records
    from the south database table.
    """
    def handle(self, *args, **kwargs):
        from south.models import MigrationHistory

        migrations = (
            '0021_auto__chg_field_appfield_label',
            '0022_auto__chg_field_membershiparchive_membership__chg_field_appfield_label',
            '0023_auto__chg_field_appfieldentry_value'
        )

        MigrationHistory.objects.filter(migration__in=migrations).delete()
