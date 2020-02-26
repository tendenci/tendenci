
import re
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Create ics file for all users
    """
    def handle(self, *args, **options):
        import os
        from django.conf import settings
        from site_settings.utils import get_setting
        from events.utils import get_vevents
        from django.contrib.auth.models import User

        p = re.compile(r'http(s)?://(www.)?([^/]+)')
        d = {}
        d['site_url'] = get_setting('site', 'global', 'siteurl')
        match = p.search(d['site_url'])
        if match:
            d['domain_name'] = match.group(3)
        else:
            d['domain_name'] = ""

        absolute_directory = os.path.join(settings.MEDIA_ROOT, 'files/ics')
        if not os.path.exists(absolute_directory):
            os.makedirs(absolute_directory)

        # Create ics file for every user
        users = User.objects.all()
        for user in users:
            ics_str = "BEGIN:VCALENDAR\n"
            ics_str += "PRODID:-//Tendenci//Tendenci Codebase 11.0 MIMEDIR//EN\n"
            ics_str += "VERSION:2.0\n"
            ics_str += "METHOD:PUBLISH\n"

            # function get_vevents in events.utils
            ics_str += get_vevents(user, d)

            ics_str += "END:VCALENDAR\n"
            file_name = 'ics-%s.ics' % (user.pk)
            file_path = os.path.join(absolute_directory, file_name)
            destination = open(file_path, 'wb+')
            destination.write(ics_str.encode())
            destination.close()
            print('Created ics for user %s pk=%s' % (user, user.pk))
