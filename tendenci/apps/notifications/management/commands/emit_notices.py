import logging

from django.core.management.base import BaseCommand

from tendenci.apps.notifications.engine import send_all


class Command(BaseCommand):
    help = "Emit queued notices."

    def handle_noargs(self, **options):
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        logging.info("-" * 72)
        send_all()
