from decimal import Decimal
import django
from django.core.cache import cache
from django.conf import settings as d_settings

from tendenci.apps.site_settings.models import Setting
from tendenci.apps.site_settings.cache import SETTING_PRE_KEY


def get_setting_key(items=[]):
    """
    Generate a setting key string from a list of string items.
    Spaces are also removed as memcached doesn't allow space characters.
    """
    if not items:
        return None

    key = ('.'.join([d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY] + items)).replace(' ', '')
    return key


def delete_all_settings_cache():
    key = get_setting_key(['all'])
    cache.delete(key)


def cache_setting(scope, scope_category, name, value):
    """
    Caches a single setting within a scope
    and scope category
    """
    key = get_setting_key([scope, scope_category, name])
    cache.set(key, value)


def cache_settings(scope, scope_category):
    """
    Caches all settings within a scope and scope category
    """
    filters = {
        'scope': scope,
        'scope_category': scope_category,
    }
    settings = Setting.objects.filter(**filters)
    if settings:
        for setting in settings:
            key = get_setting_key([setting.scope, setting.scope_category, setting.name])
            cache.set(key, setting.get_value())


def delete_setting_cache(scope, scope_category, name):
    """
        Deletes a single setting within a
        scope and scope category
    """
    key = get_setting_key([scope, scope_category, name])
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
        key = get_setting_key([setting.scope, setting.scope_category, setting.name])
        cache.delete(key)


def get_setting(scope, scope_category, name):
    """
        Gets a single setting value from within a scope
        and scope category.
        Returns the value of the setting if it exists
        otherwise it returns an empty string
    """
    key = get_setting_key([scope, scope_category, name])

    if django.apps.apps.models_ready:
        setting = cache.get(key)
    else:
        setting = None

    if setting is None:
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
        except Exception:
            setting = None

    #check if the setting has been set and evaluate the value
    if setting is not None:
        try:
            # test is get_value will work
            value = setting.get_value().strip()
        except AttributeError:
            return u''
        # convert data types
        if setting.data_type == 'boolean':
            value = value[0].lower() == 't'
        if setting.data_type == 'decimal':
            if value:
                value = Decimal(value)
            else:
                value = 0
        if setting.data_type == 'int':
            if value.strip():
                value = int(value.strip())
            else:
                value = 0  # default to 0
        if setting.data_type == 'file':
            from tendenci.apps.files.models import File as TFile
            try:
                tfile = TFile.objects.get(pk=value)
            except TFile.DoesNotExist:
                tfile = None
            value = tfile
        return value

    return u''


def get_global_setting(name):
    return get_setting('site', 'global', name)


def get_module_setting(scope_category, name):
    return get_setting('module', scope_category, name)


def check_setting(scope, scope_category, name):
    #check cache first
    key = get_setting_key([scope, scope_category, name])
    setting = cache.get(key)
    if setting is not None:
        return True

    missing_key = get_setting_key([scope, scope_category, name, "missing"])

    missing = cache.get(missing_key)
    if missing is None:
        #check the db if it is not in the cache
        exists = Setting.objects.filter(scope=scope,
            scope_category=scope_category, name=name).exists()

        #cache that it does not exist
        if not exists:
            #set to True to signify that it is missing so we do not
            #come back into this if statement and query db again
            cache.set(missing_key, True)

        return exists
    return False


def get_form_list(user):
    """
    Generate a list of 2-tuples of form id and form title
    This will be used as a special select
    """
    from tendenci.apps.forms_builder.forms.models import Form
    from tendenci.apps.perms.utils import get_query_filters
    filters = get_query_filters(user, 'forms.view_form')
    forms = Form.objects.filter(filters)
    #To avoid hitting the database n time by calling .object
    #We will use the values in the index field.
    l = []
    for form in forms:
        l.append((form.pk, form.title))

    return l


def get_box_list(user):
    """
    Generate a list of 2-tuples of form id and form title
    This will be used as a special select
    """
    from tendenci.apps.boxes.models import Box
    from tendenci.apps.perms.utils import get_query_filters
    filters = get_query_filters(user, 'boxes.view_box')
    boxes = Box.objects.filter(filters)
    #To avoid hitting the database n time by calling .object
    #We will use the values in the index field.
    l = [('', 'None')]
    for box in boxes:
        l.append((box.pk, box.title))

    return l


def get_group_list(user, show_all=False):
    """
    Generate a list of 2-tuples of group id and group name
    This will be used as a special select
    """
    from tendenci.apps.user_groups.models import Group
    groups = Group.objects.filter(status=True,
                                  status_detail='active'
                                  ).order_by('name')
    if not show_all:
        groups = groups.filter(type='distribution')
    if not groups.exists():
        # no groups - create one
        groups = [Group.objects.get_or_create_default(user)]
        initial_group = groups[0]
    else:
        [initial_group] = groups.filter(
                        entity__id=1,
                        entity__entity_name__iexact=get_global_setting(
                                                    'sitedisplayname')
                        )[:1] or [None]
        if not initial_group:
            [initial_group] = groups.filter(
                        entity__id=1)[:1] or [None]
        if not initial_group:
            initial_group = groups[0]

    choices = []

    for group in groups:
        choices.append((group.pk, group.name))

    return choices, initial_group.id
