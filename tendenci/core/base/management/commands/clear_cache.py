from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache


class Command(BaseCommand):
    """
    Clears the entire site cache
    """
    def handle(self, *args, **options):
        cache.clear()
