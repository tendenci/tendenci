# django
from django.core.cache import cache
from django.conf import settings as d_settings

# local
from site_settings.models import Setting
from site_settings.cache import SETTING_PRE_KEY

def delete_all_settings_cache():
    keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY, 'all']
    key = '.'.join(keys)
    cache.delete(key)
    
def cache_setting(scope, scope_category, name, value):
    """Caches a single setting within a scope
    and scope category
    """
    keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY, scope, 
            scope_category, name]
    key = '.'.join(keys)   
    is_set = cache.add(key, value)
    if not is_set:
        cache.set(key, value)
    
def cache_settings(scope, scope_category):
    """Caches all settings within a scope
    and scope category
    """
    filters = {
        'scope': scope,
        'scope_category': scope_category,
    }
    settings = Setting.objects.filter(**filters)
    if settings:
        for setting in settings:
            keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY,
                    setting.scope, setting.scope_category, setting.name]
            key = '.'.join(keys)
            is_set = cache.add(key, setting.value)
            if not is_set:
                cache.set(key, setting.value)

def delete_setting_cache(scope, scope_category, name):
    """
        Deletes a single setting within a
        scope and scope category
    """
    keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY, scope, 
            scope_category, name]
    key = '.'.join(keys)
    cache.delete(key)
    
def delete_settings_cache(scope, scope_category):
    """
        Deletes all settings within a scope
        and scope category
    """
    filters = {
        'scope': scope,
        'scope_category': scope_category,
    }
    settings = Setting.objects.filter(**filters)
    for setting in settings:
        keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY, 
                setting.scope, setting.scope_category, setting.name]
        key = '_'.join(keys)
        cache.delete(key)
        
def get_setting(scope, scope_category, name):
    """
        Gets a single setting value from within a scope
        and scope category.
        Returns the value of the setting if it exists
        otherwise it returns an empty string
    """
    keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY, scope,
            scope_category, name]
    key = '.'.join(keys)
    
    setting = cache.get(key)
    
    if not setting:
        #setting is not in the cache
        try:
            #try to get the setting and cache it
            filters = {
                'scope': scope,
                'scope_category': scope_category,
                'name': name
            }
            setting = Setting.objects.get(**filters)
            cache_setting(setting.scope, setting.scope_category, setting.name, setting)
        except Exception, e:
            setting = None
    
    #check if the setting has been set and evaluate the value
    if setting:
        value = setting.value.strip()
        # convert data types
        if setting.data_type == 'boolean':
            value = value[0].lower() == 't'
        if setting.data_type == 'int':
            if value.strip(): value = int(value.strip())
            else: value = 0 # default to 0
        if setting.data_type == 'file':
            from files.models import File as TFile
            try:
                tfile = TFile.objects.get(pk=value)
            except TFile.DoesNotExist:
                tfile = None
            value = tfile
        return value
    
    #return empty string as default
    return u''

def check_setting(scope, scope_category, name):
    #check cache first
    keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY, scope,
            scope_category, name]
    key = '.'.join(keys)
    
    setting = cache.get(key)
    if setting:
        return True
    
    missing_keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY, scope,
            scope_category, name, "missing"]
    missing_key = '.'.join(missing_keys)
    
    missing = cache.get(missing_key)
    if not missing:
        #check the db if it is not in the cache
        exists = Setting.objects.filter(scope=scope, 
            scope_category=scope_category, name=name).exists()

        #cache that it does not exist
        if not exists:
            #set to True to signify that it is missing so we do not
            #come back into this if statement and query db again
            is_set = cache.add(missing_key, True)
            if not is_set:
                cache.set(missing_key, True)

        return exists
    return False

def get_form_list(user):
    """
    Generate a list of 2-tuples of form id and form title
    This will be used as a special select
    """
    from forms_builder.forms.models import Form
    from perms.utils import get_query_filters
    filters = get_query_filters(user, 'forms.view_form')
    forms = Form.objects.filter(filters)
    #To avoid hitting the database n time by calling .object
    #We will use the values in the index field.
    l = [('','None')]
    for form in forms:
        l.append((form.pk, form.title))
    
    return l
    
def get_box_list(user):
    """
    Generate a list of 2-tuples of form id and form title
    This will be used as a special select
    """
    from boxes.models import Box
    from perms.utils import get_query_filters
    filters = get_query_filters(user, 'boxes.view_box')
    boxes = Box.objects.filter(filters)
    #To avoid hitting the database n time by calling .object
    #We will use the values in the index field.
    l = [('','None')]
    for box in boxes:
        l.append((box.pk, box.title))
    
    return l
