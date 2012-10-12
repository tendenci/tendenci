import re
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Scan and retrieve media files (images, pdf..) from T4 to heroku.

    Scan content for Articles, Events, News, ...
    """
    def handle(self, *apps, **kwargs):
        from tendenci.core.site_settings.utils import get_setting
        from tendenci.core.files.utils import AppRetrieveFiles

        if apps:
            apps_to_scan = apps
        else:
            apps_to_scan = ['articles', 'news', 'pages', 'jobs', 'events']
            #apps_to_scan = ['articles']

        t4_src_url = 'http://www.spegcs.org'
        site_url = get_setting('site', 'global', 'siteurl')
        # if site_url == t4_src_url, throws an error

        exts = '|'.join(['jpg', 'jpeg', 'gif', 'tif',
                           'tiff', 'bmp', 'png',
                           'pdf'])
        p = re.compile('(src|href)=\"([^"]+.(%s))\"' % exts,
                       re.IGNORECASE)

        params = {
                  'site_url': site_url,
                  'src_url': t4_src_url,
                  'p': p,
                  }
        retriever = AppRetrieveFiles(**params)

        for app in apps_to_scan:
            retriever.process_app(app)
