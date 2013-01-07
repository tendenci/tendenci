import re
import subprocess
import os
from tendenci.settings import MEDIA_ROOT
from tendenci.core.site_settings.utils import get_setting
from tendenci.addons.events.ics.models import ICS

def create_ics(user):
    try:
        from tendenci.addons.events.utils import get_vevents
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
    
        #Create ics file for user
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
    
        return ics_str
    except ImportError:
        pass


def run_precreate_ics(app_label, model_name, user):
    ics = ICS.objects.create(
        app_label=app_label,
        model_name=model_name,
        user=user
    )
    subprocess.Popen(['python', 'manage.py', 'run_precreate_ics', unicode(ics.pk)])
    return ics.pk
