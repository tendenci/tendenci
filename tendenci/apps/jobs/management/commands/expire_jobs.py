from django.core.management.base import BaseCommand
from datetime import datetime
from django.core.management import call_command
from django.utils import timezone

class Command(BaseCommand):
    """
    example: python manage.py expire_jobs
    """
    def handle(self, *args, **kwargs):
        from tendenci.apps.jobs.models import Job
        for job in Job.objects.filter(status_detail='active'):
            if job.expiration_dt < timezone.now():
                job.status_detail = 'expired'
                job.save()
        call_command('update_index', *["jobs"])
