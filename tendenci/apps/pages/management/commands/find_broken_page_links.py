import os
import re
import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Finds broken anchor links on all pages
    and prints page slug along with list of broken links
    """
    def handle(self, *args, **options):
        from tendenci.apps.pages.models import Page
        from tendenci.core.site_settings.utils import get_setting

        site_url = get_setting('site', 'global', 'siteurl')

        for page in Page.objects.all():

            urls = re.findall(r'href=[\'"]?([^\'" >]+)', page.content)

            broken_urls = []
            for url in urls:

                try:
                    if url.startswith('/'):
                        url = site_url + url

                    r = requests.head(url)
                    if not r.ok:
                        broken_urls.append(url)

                except requests.exceptions.MissingSchema:
                    pass
                except requests.exceptions.InvalidSchema:
                    pass

            print page.slug, broken_urls
