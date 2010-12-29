import os
from django.conf import settings
from django.utils import simplejson

# get the corpapp default fields list from json
def get_corpapp_default_fields_list():
    json_fields_path = os.path.join(settings.PROJECT_ROOT, 
                                    "templates/corporate_memberships/regular_fields.json")
    fd = open(json_fields_path, 'r')
    data = ''.join(fd.read())
    fd.close()
    
    if data:
        return simplejson.loads(data)
    return None
        
    