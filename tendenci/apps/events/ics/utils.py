from builtins import str
import re
import subprocess
import os
from django.conf import settings
from tendenci.libs.utils import python_executable
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.events.ics.models import ICS

def create_ics(user):
    try:
        from tendenci.apps.events.utils import get_vevents
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

        #Create ics file for user
        ics_str = "BEGIN:VCALENDAR\n"
        ics_str += "PRODID:-//Tendenci/Tendenci Codebase 11.0 MIMEDIR//EN\n"
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

        return ics_str
    except ImportError:
        pass


def run_precreate_ics(app_label, model_name, user):
    ics = ICS.objects.create(
        app_label=app_label,
        model_name=model_name,
        user=user
    )
    subprocess.Popen([python_executable(), 'manage.py', 'run_precreate_ics', str(ics.pk)])
    return ics.pk
