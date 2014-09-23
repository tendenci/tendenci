import subprocess
import time as ttime
from datetime import datetime, date, time

from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils.encoding import smart_str

from tendenci.addons.articles.models import Article
from tendenci.core.base.utils import normalize_newline, UnicodeWriter
from tendenci.core.emails.models import Email
from tendenci.core.site_settings.utils import get_setting

def process_export(identifier, user_id):
    field_list = [
            'guid',
            'slug',
            'timezone',
            'headline',
            'summary',
            'body',
            'source',
            'first_name',
            'last_name',
            'phone',
            'fax',
            'email',
            'website',
            'release_dt',
            'syndicate',
            'featured',
            'design_notes',
            'tags',
            'enclosure_url',
            'enclosure_type',
            'enclosure_length',
            'not_official_content',
            'entity',
        ]

    identifier = identifier or int(ttime.time())
    file_name_temp = 'export/articles/%s_temp.csv' % (identifier)

    with default_storage.open(file_name_temp, 'wb') as csvfile:
        csv_writer = UnicodeWriter(csvfile, encoding='utf-8')
        csv_writer.writerow(field_list)

        articles = Article.objects.filter(status_detail='active')

        for article in articles:
            items_list = []
            for field_name in field_list:
                item = getattr(article, field_name)

                if isinstance(item, datetime):
                    item = item.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(item, date):
                    item = item.strftime('%Y-%m-%d')
                elif isinstance(item, time):
                    item = item.strftime('%H:%M:%S')
                elif isinstance(item, basestring):
                    item = item.encode("utf-8")
                item = smart_str(item).decode('utf-8')
                items_list.append(item)
            csv_writer.writerow(items_list)

    # rename the file name
    file_name = 'export/articles/%s.csv' % identifier
    default_storage.save(file_name, default_storage.open(file_name_temp, 'rb'))

    # delete the temp file
    default_storage.delete(file_name_temp)

    # notify user that export is ready to download
    [user] = User.objects.filter(pk=user_id)[:1] or [None]
    if user and user.email:
        download_url = reverse('article.export_download', args=[identifier])

        site_url = get_setting('site', 'global', 'siteurl')
        site_display_name = get_setting('site', 'global', 'sitedisplayname')
        parms = {
            'download_url': download_url,
            'user': user,
            'site_url': site_url,
            'site_display_name': site_display_name,
            'date_today': datetime.now()}

        subject = render_to_string(
            'articles/notices/export_ready_subject.html', parms)
        subject = subject.strip('\n').strip('\r')

        body = render_to_string(
            'articles/notices/export_ready_body.html', parms)

        email = Email(
            recipient=user.email,
            subject=subject,
            body=body)
        email.send()