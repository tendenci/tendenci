import commands
from django.conf import settings
from django.core.management.base import BaseCommand
from datetime import datetime

class Command(BaseCommand):
    """
    example: python manage.py expire_resumes
    """
    def handle(self, *args, **kwargs):
        from resumes.models import Resume
        for resume in Resume.objects.filter(status_detail='active'):
            if resume.expiration_dt < datetime.now():
                resume.status_detail = 'expired'
                resume.save()
