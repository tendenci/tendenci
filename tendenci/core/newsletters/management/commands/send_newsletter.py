from optparse import make_option
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Newsletter sending

    Usage:
        python manage.py send_newsletter

        example:
        python manage.py send_newsletter --newsletter 1

    """
    option_list = BaseCommand.option_list + (

        make_option(
            '--newsletter',
            action='store',
            dest='newsletter',
            help='Newsletter ID'),

    )

    def handle(self, *args, **options):
        from tendenci.core.newsletters.models import Newsletter

        newsletter_id = options.get('newsletter', 0)

        if newsletter_id == 0:
            raise CommandError('Newsletter ID is required. Usage: ./manage.py send_newsletter --newsletter 1')

        newsletter = Newsletter.objects.filter(pk=int(newsletter_id))
        if newsletter.exists():
            newsletter = newsletter[0]
        else:
            newsletter = None

        if not newsletter:
            raise CommandError('You are trying to send a newsletter that does not exist.')
