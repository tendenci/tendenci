import os
from celery.task import Task
from celery.registry import tasks
from BeautifulSoup import BeautifulStoneSoup
from parse_uri import ParseUri
from tendenci.apps.wp_importer.utils import get_media, get_posts, get_pages
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.template import RequestContext

class WPImportTask(Task):

    def run(self, file_name, request, **kwargs):
        """
        Parse the given xml file using BeautifulSoup. Save all Article, Redirect and Page objects.
        """
        user = request.user
        f = open(file_name, 'r')
        xml = f.read()
        f.close()

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
        
        if user.email:
            context_instance = RequestContext(request)
            context_instance.autoescape = False
            subject = ''.join(render_to_string(('notification/wp_import/short.txt'), context_instance).splitlines())

            context_instance = RequestContext(request)
            context_instance.autoescape = True
            body = render_to_string(('notification/wp_import/full.html'), context_instance)

            #send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
            email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
            email.content_subtype = 'html'
            email.send(fail_silently=True)

tasks.register(WPImportTask)
