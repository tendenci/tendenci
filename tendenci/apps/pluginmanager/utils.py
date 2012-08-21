import re
import shutil
import os
import sys
from optparse import make_option, OptionParser

from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import color_style
from django.utils.encoding import smart_str
from django.conf import settings

def copy_helper(style, app_or_project, app_cap_single, app_low_single, app_cap_plural, app_low_plural, ev_id, other_name=''):
    """
    Copies either a Django application layout template or a Django project
    layout template into the specified directory.

    """
    # style -- A color style object (see django.core.management.color).
    # app_or_project -- The string 'app' or 'project'.
    # name -- The name of the application or project.
    # directory -- The directory to which the layout template should be copied.
    # other_name -- When copying an application layout, this should be the name
    #               of the project.
    
    app_or_project = 'plugin'
    directory = 'plugins'
    if not re.search(r'^[_a-zA-Z]\w*$', app_low_plural): # If it's not a valid directory name.
        # Provide a smart error message, depending on the error.
        if not re.search(r'^[_a-zA-Z]', app_low_plural):
            message = 'make sure the name begins with a letter or underscore'
        else:
            message = 'use only numbers, letters and underscores'
        raise CommandError("%r is not a valid %s name. Please %s." % (app_low_plural, app_or_project, message))
    top_dir = os.path.join(directory, app_low_plural)
    try:
        os.mkdir(top_dir)
    except OSError, e:
        pass

    # Determine where the app or project templates are. Use
    # django.__path__[0] because we don't know into which directory
    # django has been installed.
    template_dir = os.path.join(settings.PROJECT_ROOT, 'plugins', 'plugin_template')

    for d, subdirs, files in os.walk(template_dir):
        relative_dir = d[len(template_dir)+1:]
        if relative_dir:
            print relative_dir
            os.mkdir(os.path.join(top_dir, relative_dir.replace('plugin_template', app_low_plural)))
        for subdir in subdirs[:]:
            print subdir
            if subdir.startswith('.'):
                subdirs.remove(subdir)
        for f in files:
            if not f.endswith(('.py','.html','.txt')):
                # Ignore .pyc, .pyo, .py.class etc, as they cause various
                # breakages.
                continue
            path_old = os.path.join(d, f)
            path_new = os.path.join(top_dir, relative_dir.replace('plugin_template', app_low_plural), f.replace('S_P_LOW', app_low_plural).replace('S_S_LOW', app_low_single))
            fp_old = open(path_old, 'r')
            fp_new = open(path_new, 'w')
            fp_new.write(fp_old.read().replace('S_S_LOW', app_low_single).replace('S_P_LOW', app_low_plural).replace('S_S_CAP', app_cap_single).replace('S_P_CAP', app_cap_plural).replace('EVID', ev_id))
            fp_old.close()
            fp_new.close()
            try:
                shutil.copymode(path_old, path_new)
                _make_writeable(path_new)
            except OSError:
                sys.stderr.write(style.NOTICE("Notice: Couldn't set permission bits on %s. You're probably using an uncommon filesystem setup. No problem.\n" % path_new))

def _make_writeable(filename):
    """
    Make sure that the file is writeable. Useful if our source is
    read-only.

    """
    import stat
    if sys.platform.startswith('java'):
        # On Jython there is no os.access()
        return
    if not os.access(filename, os.W_OK):
        st = os.stat(filename)
        new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
        os.chmod(filename, new_permissions)


def update_addons(installed_apps):
    # Try used only for the first install when PluginApp
    # table does not exist yet.
    try:
        from tendenci.apps.pluginmanager.models import PluginApp
        add_new_addons(installed_apps)

        # Append only enabled addons to the INSTALLED_APPS
        addons = PluginApp.objects.filter(is_enabled=True)
        installed_addons = tuple([i.package for i in addons])
        installed_apps += installed_addons
    except:
        pass

    return installed_apps


def add_new_addons(installed_apps):
    """
    Adds new addons to the database
    """
    from tendenci.apps.pluginmanager.models import PluginApp
    new_addons = []
    tendenci_addons = sorted(tendenci_choices())
    for addon in tendenci_addons:
        addon_package = '.'.join(['tendenci', 'addons', addon])
        if addon_package not in installed_apps:
            try:
                PluginApp.objects.get(package=addon_package)
            except:
                new_addons.append({'package': addon_package, 'title': addon.title().replace('_', ' '), 'description': ''})

    custom_addons = sorted(custom_choices())
    for addon in custom_addons:
        print addon
        addon_package = '.'.join(['addons', addon])
        try:
            PluginApp.objects.get(package=addon_package)
        except:
            new_addons.append({'package': addon_package, 'title': addon.title().replace('_', ' '), 'description': ''})

    # Add new addons to the database
    for addon in new_addons:
        PluginApp.objects.create(package=addon['package'], title=addon['title'], description=addon['description'], is_enabled=False)

    return new_addons


def plugin_options():
    """
    Returns a string of the available themes in THEMES_DIR
    """
    tendenci_options = []
    tendenci_addons = sorted(tendenci_choices())
    for addon in tendenci_addons:
        addon_package = '.'.join(['tendenci', 'addons', addon])
        if addon_package not in settings.INSTALLED_APPS:
            tendenci_options.append((addon_package, addon.title().replace('_', ' ')))

    custom_options = []
    custom_addons = sorted(custom_choices())
    for addon in custom_addons:
        print addon
        addon_package = '.'.join(['addons', addon])
        if addon_package not in settings.INSTALLED_APPS:
            custom_options.append((addon_package, addon.title().replace('_', ' ')))

    if custom_options:
        return (('Custom', custom_options), ('Tendenci', tendenci_options))
    else:
        return tendenci_options


def tendenci_choices():
    """
    Returns a list of available addons in tendenci app
    """
    for addon in os.listdir(settings.ADDONS_PATH):
        if os.path.isdir(os.path.join(settings.ADDONS_PATH, addon)):
            yield addon


def custom_choices():
    """
    Returns a list of available addons in the tendenci-site wrapper app
    """
    for addon in os.listdir(settings.SITE_ADDONS_PATH):
        if os.path.isdir(os.path.join(settings.SITE_ADDONS_PATH, addon)):
            yield addon
