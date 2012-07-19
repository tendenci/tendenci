import os
from django.utils import simplejson
from django.utils.encoding import smart_str

def rel(*x):
    #return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)
    # cannot import settings.py in this file 'cause it is called by setting.
    # it is ugly but there is no other way unless we move this file to the same location where apps.json is. - GJQ
    return os.path.join(os.path.join(os.path.split(os.path.split(os.path.abspath(os.path.dirname(__file__)))[0])[0], 'plugins'), *x)

def get_apps():
    """ Get apps from json files"""
    apps = []
    #json_data_path = rel('plugins.json')
    json_data_path = rel('apps.json')
    
    #print 'json_data_path = ', json_data_path
    if not os.path.exists(json_data_path):
        #print 'Not exist'
        return apps

    if not os.path.isfile(json_data_path):
        #print 'Not file'
        return apps

    f = open(json_data_path, 'r')
    data = ''.join(f.read()) #TODO: must understand unicode
    if not data:
        #print 'No apps'
        return apps

    json_data = simplejson.loads(data)
    #print 'json_data=', json_data
    return json_data

def plugin_apps(installed_apps):
    apps = tuple(smart_str(i['package']) for i in get_apps() if i['is_enabled'])
    #print 'apps = ', apps
    return installed_apps + apps
    
