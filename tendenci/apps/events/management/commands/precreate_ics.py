import re
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Create ics file for all users
    """
    def handle(self, *args, **options):
        import os
        from Tendenci50.settings import MEDIA_ROOT
        from site_settings.utils import get_setting
        from events.models import Event
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

        absolute_directory = os.path.join(MEDIA_ROOT, 'files/ics')
        if not os.path.exists(absolute_directory):
            os.makedirs(absolute_directory)

        # Create ics file for every user
        users = User.objects.all()
        user = User.objects.get(pk='1')
        #for user in users:
        ics_str = "BEGIN:VCALENDAR\n"
        ics_str += "PRODID:-//Schipul Technologies//Schipul Codebase 5.0 MIMEDIR//EN\n"
        ics_str += "VERSION:2.0\n"
        ics_str += "METHOD:PUBLISH\n"

        # function get_vevents in events.utils
        ics_str += get_vevents(user, d)

        ics_str += "END:VCALENDAR\n"
        ics_str = ics_str.encode('UTF-8')
        file_name = 'ics-%s.ics' % (user.pk)
        file_path = os.path.join(absolute_directory, file_name)
        destination = open(file_path, 'w+')
        destination.write(ics_str)
        destination.close()
        print 'Created ics for user %s pk=%s' % (user, user.pk)
