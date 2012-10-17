import re
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Scan and retrieve media files (images, pdf..) from T4 to heroku.

    Scan content for Articles, News, Pages, Jobs and Events.

    Example:
        ./manage.py scan_and_retrieve_files articles pages --src_url=http://www.YourOldSite.com
    """
    option_list = BaseCommand.option_list + (
        make_option('--src_url',
            action='store',
            dest='src_url',
            default=None,
            help='src_url from which the files being downloaded'),
        )

    def handle(self, *apps, **kwargs):
        from tendenci.core.site_settings.utils import get_setting
        from tendenci.core.files.utils import AppRetrieveFiles

        if apps:
            apps_to_scan = apps
        else:
            apps_to_scan = ['articles', 'news', 'pages', 'jobs', 'events']
            #apps_to_scan = ['articles']

        site_url = get_setting('site', 'global', 'siteurl')
        #src_url = 'http://www.spegcs.org'
        src_url = kwargs['src_url']
        if not src_url:
            raise CommandError('--src_url is required')

        if src_url == site_url:
            raise CommandError('src_url cannot be the same as the site_url')

        exts = '|'.join(['jpg', 'jpeg', 'gif', 'tif',
                           'tiff', 'bmp', 'png',
                           'pdf', 'doc', 'xls',
                           'ppt', 'pps', 'mp3',
                           'mp4', 'zip', 'docx',
                           'pptx', 'xlsx', 'wpd',
                           'wp5', 'txt', 'csv',
                           'rtf', 'avi', 'mov',
                           'mpe', 'mpg', 'mpeg',
                           'wmv', 'xml', 'swf',
                           'flv', 'fla'])
        p = re.compile('(src|href)=\"([^"]+.(%s))\"' % exts,
                       re.IGNORECASE)

        params = {
                  'site_url': site_url,
                  'src_url': src_url,
                  'p': p,
                  }
        retriever = AppRetrieveFiles(**params)

        for app in apps_to_scan:
            retriever.process_app(app)

        if retriever.broken_links:
            print '\nBROKEN LINKS:\n', '-' * 30
            for key in retriever.broken_links.keys():
                print
                print key
                for link in retriever.broken_links[key]:
                    print ' ' * 4, link
