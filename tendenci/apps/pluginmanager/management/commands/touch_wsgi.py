import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        from django.conf import settings
        wsgi = getattr(settings, "WSGI_PATH", None)
        if wsgi:
            os.system('touch ' + wsgi)
