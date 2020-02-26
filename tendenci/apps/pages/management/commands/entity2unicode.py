import re
from html import parser as html_parser
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
        self.h = html_parser.HTMLParser()
        pattern = re.compile(r'(&#\d+;)', re.IGNORECASE)

        for page in pages:
            page.title = re.sub(pattern, self.unescape, page.title)
            page.content = re.sub(pattern, self.unescape, page.content)
            page.save()
