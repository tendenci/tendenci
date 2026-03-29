from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone

class Command(BaseCommand):
    """
    example: python manage.py expire_stories
    """
    def handle(self, *args, **kwargs):
        from tendenci.apps.stories.models import Story
        for story in Story.objects.filter(expires=True, status_detail='active'):
            if story.end_dt and story.end_dt < timezone.now():
                story.status_detail = 'expired'
                story.save()
        call_command('update_index', *["stories"])
