import os
from celery.task import Task
from celery.registry import tasks
from BeautifulSoup import BeautifulStoneSoup
from parse_uri import ParseUri
from wp_importer.utils import get_media, get_posts, get_pages

class WPImportTask(Task):

    def run(self, file_name, user, **kwargs):
        """
        Parse the given xml file using BeautifulSoup. Save all Article, Redirect and Page objects.
        """
        f = open(file_name, 'r')
        xml = f.read()
        f.close()
        os.remove(file_name)

        uri_parser = ParseUri()
        soup = BeautifulStoneSoup(xml)
        items = soup.findAll('item')

        for item in items:
            post_type = item.find('wp:post_type').string
            post_status = item.find('wp:status').string

            if post_type == 'attachment':
                get_media(item, uri_parser, user)
                # Note! This script assumes all the attachments come before
                # posts and pages in the xml. If this ends up changing,
                # do two loops, one with attachments and the second with posts and pages.
            elif post_type == 'post' and post_status == 'publish':
                get_posts(item, uri_parser, user)
            elif post_type == 'page' and post_status == 'publish':
                get_pages(item, uri_parser, user)


tasks.register(WPImportTask)
