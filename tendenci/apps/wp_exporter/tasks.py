import os
from celery.task import Task
from celery.registry import tasks
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.base import ContentFile

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.wp_exporter.models import XMLExport
from tendenci.apps.wp_exporter.utils import gen_xml

class WPExportTask(Task):

    def run(self, form, user, **kwargs):
        xml = gen_xml(form.cleaned_data)
        file_content = ContentFile(xml.content.encode(encoding='UTF-8',errors='strict'))

        export = XMLExport()
        export.author = user
        export.xml.save('export.xml', file_content, save=True)

        if user.email:
            context_instance = {
                'SITE_GLOBAL_SITEDISPLAYNAME': get_setting('site', 'global', 'sitedisplayname'),
                'SITE_GLOBAL_SITEURL': get_setting('site', 'global', 'siteurl'),
                'export': export,
            }
            subject = ''.join(render_to_string(('notification/wp_export/short.txt'), context_instance).splitlines())
            body = render_to_string(('notification/wp_export/full.html'), context_instance)

            #send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
            email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
            email.content_subtype = 'html'
            email.send(fail_silently=True)

tasks.register(WPExportTask)
