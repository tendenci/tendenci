import commands
from django.conf import settings
from django.core.management.base import BaseCommand
from datetime import datetime

class Command(BaseCommand):
    """
    example: python manage.py expire_jobs
    """
    def handle(self, *args, **kwargs):
        from jobs.models import Job
        for job in Job.objects.filter(status_detail='active'):
            if job.expiration_dt < datetime.now():
                job.status_detail = 'expired'
                job.save()
