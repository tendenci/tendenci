import os

from django.core.urlresolvers import reverse
from django.utils.functional import lazy
from django.conf import settings
from django.conf.urls.defaults import patterns, include

from tendenci.core.site_settings.utils import check_setting, get_setting

lazy_reverse = lazy(reverse, str)


class RegisteredApps(object):
    """
    RegistredApps iterarable that represents all registered apps

    All registered apps exist in the objects iterable and are also
    categorized by core/plugins.

    apps = site.get_registered_apps()

    core_apps = registered_apps.core
    addon_apps = registered_apps.addon
    people_apps = registered_apps.people
    """
    def __init__(self, apps, build_from_cache=False):
        self.all_apps = []
        self.core = []
        self.addons = []
        self.people = []

        # append core and plugin apps to
        # individual lists
        if not build_from_cache:
            for model, registry in apps.items():

                setting_tuple = (
                    'module',
                    registry.fields['model']._meta.app_label,
                    'enabled',
                )

                # enabled / has settings
                if check_setting(*setting_tuple):
                    registry.fields['enabled'] = get_setting(*setting_tuple)
                    registry.fields['has_settings'] = True
                else:
                    registry.fields['enabled'] = True
                    registry.fields['has_settings'] = False

                if not 'settings' in registry.fields['url'].keys():
                    registry.fields['url'].update({
                        'settings': lazy_reverse('settings.index', args=[
                            'module',
                            registry.fields['model']._meta.app_label
                        ])
                    })

                if registry.fields['app_type'] == 'addon':
                    self.addons.append(registry.fields)

                if registry.fields['app_type'] == 'people':
                    self.people.append(registry.fields)

                if registry.fields['app_type'] == 'core':
                    self.core.append(registry.fields)

                # append all apps for main iterable
                self.all_apps.append(registry.fields)
        else:
            #since we can only cache the list of apps and not the RegisteredApps instance
            #we have to rebuild this object based on the list of apps from the cache.
            for app in apps:

                setting_tuple = (
                    'module',
                    app['model']._meta.app_label,
                    'enabled',
                )

                # enabled / has settings
                if check_setting(*setting_tuple):
                    app['enabled'] = get_setting(*setting_tuple)
                    app['has_settings'] = True
                else:
                    app['enabled'] = True
                    app['has_settings'] = False

                if not 'settings' in app['url'].keys():
                    app['url'].update({
                        'settings': lazy_reverse('settings.index', args=[
                            'module',
                            app['model']._meta.app_label
                        ])
                    })

                if app['app_type'] == 'addon':
                    self.addons.append(app)

                if app['app_type'] == 'people':
                    self.people.append(app)

                if app['app_type'] == 'core':
                    self.core.append(app)

                # append all apps for main iterable
                self.all_apps.append(app)

        # sort the applications alphabetically by
        # object representation
        key = lambda x: unicode(x)
        self.all_apps = sorted(self.all_apps, key=key)
        self.core = sorted(self.core, key=key)
        self.addons = sorted(self.addons, key=key)
        self.people = sorted(self.people, key=key)

    def __iter__(self):
        return iter(self.all_apps)

    def __len__(self):
        return len(self.all_apps)


def update_addons(installed_apps, addon_folder_path):
    # Append only enabled addons to the INSTALLED_APPS
    addons = get_addons(installed_apps, addon_folder_path)
    installed_addons = tuple([i for i in addons])
    installed_apps += installed_addons

    return installed_apps


def get_addons(installed_apps, addon_folder_path):
    """
    Grabs a list of apps that aren't in INSTALLED_APPS
    """
    new_addons = []

    custom_addons = sorted(custom_choices(addon_folder_path))
    for addon in custom_addons:
        addon_package = '.'.join(['addons', addon])
        try:
            __import__(addon_package)
            new_addons.append(addon_package)
        except:
            pass

    return new_addons


def custom_choices(addon_folder_path):
    """
    Returns a list of available addons in the tendenci-site wrapper app
    """
    for addon in os.listdir(addon_folder_path):
        if os.path.isdir(os.path.join(addon_folder_path, addon)):
            yield addon


def get_url_patterns():
    items = []
    addons = get_addons(settings.INSTALLED_APPS, settings.SITE_ADDONS_PATH)
    for addon in addons:
        try:
            __import__('.'.join([addon, 'urls']))
            items.append((r'', include('%s.urls' % addon,)))
        except:
            pass

    return patterns('', *items)
    pass
