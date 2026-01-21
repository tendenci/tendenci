
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    """
    Send forum digest (daily or weekly) to all forum subscribers who opted in.
    
    Usage:
        For daily digest, schedule the command to run daily.
            python manage.py send_forum_digest --digest_type daily
        
        For weekly digest, schedule the command to run weekly.
        python manage.py send_forum_digest --digest_type weekly
    """
    def add_arguments(self, parser):
        parser.add_argument('--digest_type',
            dest='digest_type',
            default=None,
            help='digest_type - either daily or weekly')

    def handle(self, *args, **options):
        from tendenci.apps.forums.models import Forum
        digest_type = options.get('digest_type', None)
        if not digest_type:
            raise CommandError('Exiting.. no digest_type is specified.')
        for forum in Forum.objects.all():
            forum.send_digest_to_subscribers(digest_type)
        