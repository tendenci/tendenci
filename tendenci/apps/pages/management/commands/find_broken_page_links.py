
import requests
from requests.exceptions import (
    MissingSchema, InvalidSchema, InvalidURL, ConnectionError)
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import LocationParseError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Finds broken anchor links on all pages
    and prints page slug along with list of broken links
    """
    COMMON_EXCEPTIONS = (
        MissingSchema,
        InvalidSchema,
        InvalidURL,
        ConnectionError,
        LocationParseError)

    def get_broken_links(self, links):
        """
        Returns a list of broken links
        """
        broken_links = []
        for link in links:

            url = link.get('href', '')

            try:
                if url.startswith('/'):
                    url = self.SITE_URL + url

                r = requests.head(url)
                if not r.ok:
                    broken_links.append(link)

            except self.COMMON_EXCEPTIONS:
                pass

        return broken_links

    def get_broken_images(self, images):
        """
        Returns a list of broken links
        """
        broken_images = []
        for image in images:

            src = image.get('src')

            try:
                if src.startswith('/'):
                    src = self.SITE_URL + src

                r = requests.head(src, timeout=10)
                if not r.ok:
                    broken_images.append(image)

            except self.COMMON_EXCEPTIONS:
                pass

        return broken_images

    def handle(self, *args, **options):
        from tendenci.apps.pages.models import Page
        from tendenci.apps.site_settings.utils import get_setting

        self.SITE_URL = get_setting('site', 'global', 'siteurl')

        for page in Page.objects.all():

            soup = BeautifulSoup(page.content)

            links = soup.find_all('a')
            # images = soup.find_all('img')

            broken_links = self.get_broken_links(links)
            # broken_images = self.get_broken_images(images)

            # print(page.slug)
            # print('images', '%s/%s' % (len(images), len(broken_images)))
            # print('links', '%s/%s' % (len(links), len(broken_links)), broken_links)

            print(page.slug, broken_links)
