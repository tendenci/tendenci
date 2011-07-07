from createsend import Client
from django.conf import settings
from site_settings.utils import get_setting
from campaign_monitor.models import Template
import urllib2
import random
import string

api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None)
api_password = getattr(settings, 'CAMPAIGNMONITOR_API_PASSWORD', None)
client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)

def random_string(n=32):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(n))
    
def temporary_id():
    exists = True
    while(exists):
        id = random_string()
        if not Template.objects.filter(template_id=id).exists():
            exists = False
    return id
