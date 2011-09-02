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
    shutil.rmtree(plugin_dir, ignore_errors=True)
    os.mkdir(plugin_dir)
    init = open(os.path.join(plugin_dir, '__init__.py'), 'w')
    init.close()
    build_models(plugin, plugin_dir)
    build_forms(plugin, plugin_dir)
    build_search_indexes(plugin, plugin_dir)
    build_search_document(plugin, plugin_dir)

def build_models(plugin, plugin_dir):
    """
    Create plugin's models.py
    """
    
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
    """
    Create plugins forms.py
    """
    
    top = open(os.path.join(TEMPLATE_ROOT, 'forms', 'top.txt')).read()
    forms = open(os.path.join(plugin_dir, 'forms.py'), 'w')
    forms.write(render_to_plugin(top, plugin))
    for field in plugin.fields.all():
        type = field.type.split('/')[1]
        if type == "Wysiwyg":
            forms.write(
                "    %s = forms.CharField(required=%s," \
                % (field.name, field.blank)
            )
            forms.write(
                "widget=TinyMCE(attrs={'style':'width:100%'},"
            )
            forms.write(
                "mce_attrs={'storme_app_label':%r," % plugin.plural_lower
            )
            forms.write(
                "'storme_model':%s._meta.module_name.lower()})\n" \
                % plugin.single_caps
            )
        if type == "DateTimeField":
            forms.write(
                "    %s = SplitDateTimeField(required=%s)" \
                % (field.name, field.blank)
            )
    forms.close()
    
def build_search_indexes(plugin, plugin_dir):
    """
    Creates plugin's search_indexes.py
    """
    
    top = open(os.path.join(TEMPLATE_ROOT, 'search_indexes', 'top.txt')).read()
    bottom = open(os.path.join(TEMPLATE_ROOT, 'search_indexes', 'bottom.txt')).read()
    index = open(os.path.join(plugin_dir, 'search_indexes.py'), 'w')
    index.write(render_to_plugin(top, plugin))
    for field in plugin.fields.all():
        type = field.type.split('/')[2]
        index.write(
            "    %s = indexes.%s(model_attr='%s')\n" \
            % (field.name, type, field.name)
        )
    index.close()

def build_search_document(plugin, plugin_dir):
    """
    Creates the plugin's document for the search index.
    """
    top = open(os.path.join(TEMPLATE_ROOT, 'search_document', 'top.txt')).read()
    document_path = os.path.join(plugin_dir, 'templates', 'search', plugin.plural_lower)
    os.makedirs(document_path)
    document = open(os.path.join(document_path, '%s.txt' % plugin.single_caps.lower()), 'w')
    document.write(render_to_plugin(top, plugin))
    for field in plugin.fields.all():
        document.write("{{ object.%s }}\n"%field.name)
    document.close()
    
