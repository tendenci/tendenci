import re
import HTMLParser
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Converts title and content html entities to unicode
    """

    def unescape(self, *args, **kwargs):
        match = args[0]
        entity = match.group(1)
        return self.h.unescape(entity)

    def handle(self, *args, **options):
        from tendenci.apps.pages.models import Page

        pages = Page.objects.all()
        self.h = HTMLParser.HTMLParser()
        pattern = re.compile('(&#\d+;)', re.IGNORECASE)

        for page in pages:
            page.title = re.sub(pattern, self.unescape, page.title)
            page.content = re.sub(pattern, self.unescape, page.content)
            page.save()
