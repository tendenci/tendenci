import re
import shutil
import os
import sys
from optparse import make_option, OptionParser

from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import color_style
from django.utils.encoding import smart_str
from django.conf import settings

TEMPLATE_ROOT = os.path.join(settings.PROJECT_ROOT, 'templates', 'plugin_builder')

def render_to_plugin(temp, plugin):
    return temp.replace('S_P_LOW', plugin.plural_lower)\
        .replace('S_S_CAP', plugin.single_caps)\
        .replace('S_S_LOW', plugin.single_lower)\
        .replace('S_P_CAP', plugin.plural_caps)
    

def build_plugin(plugin):
    """
    plugin should be a plugin_builder.models.Plugin
    Creates a tendenci plugin based on the the given plugin.
    """
    
    plugin_dir = os.path.join(settings.PROJECT_ROOT, 'plugins', plugin.plural_lower)
    os.mkdir(plugin_dir)
    init = open(os.path.join(plugin_dir, '__init__.py'), 'w')
    init.close()
    build_models(plugin, plugin_dir)

def build_models(plugin, plugin_dir):
    top = open(os.path.join(TEMPLATE_ROOT, 'models', 'top.txt')).read()
    bottom = open(os.path.join(TEMPLATE_ROOT, 'models', 'bottom.txt')).read()
    models = open(os.path.join(plugin_dir, 'models.py'), 'w')
    models.write(render_to_plugin(top, plugin))
    for field in plugin.fields.all():
        type = field.type.split('/')[0]
        models.write(
            "    %s = models.%s(_(%r),default=%r, help_text=%r, blank=%s)\n" \
            % (field.name, type, field.name, field.default, field.help_text, field.blank)
        )
    models.write(render_to_plugin(bottom, plugin))
    models.close()
    
def build_forms(plugin, plugin_dir):
    forms = open(os.path.join(plugin_dir, 'forms.py'), 'w')
    
def build_search_index(plugin, plugin_dir):
    index = open(os.path.join(plugin_dir, 'search_indexes.py'), 'w')
