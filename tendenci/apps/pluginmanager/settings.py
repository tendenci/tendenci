import os
from django.utils import simplejson
from django.utils.encoding import smart_str

def get_apps(local_root):
    """ Get apps from json files"""
    apps = []

    json_data_path = os.path.join(local_root, 'addons_list.json')

    if not os.path.exists(json_data_path):
        return apps

    if not os.path.isfile(json_data_path):
        return apps

    f = open(json_data_path, 'r')
    data = ''.join(f.read())  #TODO: must understand unicode
    if not data:
        return apps

    json_data = simplejson.loads(data)

    return json_data

def plugin_apps(installed_apps, local_root):
    apps = tuple(smart_str(i['package']) for i in get_apps(local_root) if i['is_enabled'])

    return installed_apps + apps
