from django.core.management.base import BaseCommand
from django.db.models.loading import get_models
from django.core.management import call_command
from django.contrib.auth.models import User
from django.conf import settings

class Command(BaseCommand):
    """
    Add missing ud fields ud6, ...ud30 to a membership app

    Usage:
        .manage.py add_ud_fields_to_mem_app 1
    """
    def add_arguments(self, parser):
        parser.add_argument('app_id', type=int)

    def handle(self, *args, **options):
        from tendenci.apps.memberships.models import MembershipAppField
        
        app_id = options['app_id']
        po = 92
        for i in xrange(6, 31):
            if not MembershipAppField.objects.filter(
                                membership_app_id=app_id,
                                field_name='ud%s' % i).exists():
                app_field = MembershipAppField(
                                 membership_app_id=app_id,
                                 field_name='ud%s' % i,
                                 label='User Defined %s' % i,
                                 position=po,
                                 display=False)
                app_field.save()
                po += 1
