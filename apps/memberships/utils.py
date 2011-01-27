import os
from django.conf import settings
from django.utils import simplejson

def get_default_membership_fields():
    json_file_path = os.path.join(settings.PROJECT_ROOT,
        'apps/memberships/fixtures/default_membership_application_fields.json')
    json_file = open(json_file_path, 'r')
    data = ''.join(json_file.read())
    json_file.close()

    if data:
        return simplejson.loads(data)
    return None