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
        .replace('S_P_CAP', plugin.plural_caps)\
        .replace('EVID', str(plugin.event_id))

def build_plugin(plugin):
    """
    plugin should be a plugin_builder.models.Plugin
    Creates a tendenci plugin based on the the given plugin.
    If the plugin already exists, remove it then rebuild.
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
    build_template_tags(plugin, plugin_dir)
    build_templates(plugin, plugin_dir)
    build_admin(plugin, plugin_dir)
    build_the_rest(plugin, plugin_dir)

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
            "    %s = models.%s(_(%r), help_text=%r, blank=%s," \
            % (field.name, type, field.name, field.help_text, not(field.required))
        )
        #add max_length for charfield
        if type == 'CharField':
            models.write(" max_length=200,")
        #add default param
        if type == 'IntegerField':
            models.write(" default=%s,"%field.default)
        else:
            models.write(" default=%r,"%field.default)
        #add extra kwargs
        if field.kwargs:
            models.write(" %s)\n"%field.kwargs)
        else:
            models.write(")\n")
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
                % (field.name, field.required)
            )
            forms.write(
                "widget=TinyMCE(attrs={'style':'width:100%'},"
            )
            forms.write(
                "mce_attrs={'storme_app_label':%r," % plugin.plural_lower
            )
            forms.write(
                "'storme_model':%s._meta.module_name.lower()}))\n" \
                % plugin.single_caps
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
    index.write(render_to_plugin(bottom, plugin))
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
    
def build_template_tags(plugin, plugin_dir):
    """
    Creates the plugin's template tags.
    """
    tags_path = os.path.join(plugin_dir, 'templatetags')
    os.mkdir(tags_path)
    tags_text = open(os.path.join(TEMPLATE_ROOT, 'template_tags.txt')).read()
    init = open(os.path.join(tags_path, '__init__.py'), 'w')
    init.close()
    tags = open(os.path.join(tags_path, '%s_tags.py' % plugin.plural_lower), 'w')
    tags.write(render_to_plugin(tags_text, plugin))
    tags.close()
    
def build_templates(plugin, plugin_dir):
    """
    Creates the plugin's templates.
    """
    templates_path = os.path.join(plugin_dir, 'templates', plugin.plural_lower)
    os.makedirs(templates_path)
    
    base_text = open(os.path.join(TEMPLATE_ROOT, 'templates', 'base.html')).read()
    base = open(os.path.join(templates_path, 'base.html'), 'w')
    base.write(render_to_plugin(base_text, plugin))
    base.close()
    
    search_text = open(os.path.join(TEMPLATE_ROOT, 'templates', 'search.html')).read()
    search = open(os.path.join(templates_path, 'search.html'), 'w')
    search.write(render_to_plugin(search_text, plugin))
    search.close()
    
    #build detail.html
    top = open(os.path.join(TEMPLATE_ROOT, 'templates', 'detail', 'top.txt')).read()
    bottom = open(os.path.join(TEMPLATE_ROOT, 'templates', 'detail', 'bottom.txt')).read()
    detail = open(os.path.join(templates_path, 'detail.html'), 'w')
    detail.write(render_to_plugin(top, plugin))
    for field in plugin.fields.all():
        detail.write("<div>{{ %s.%s }}</div>\n"% (plugin.single_lower, field.name))
    detail.write(render_to_plugin(bottom, plugin))
    detail.close()
    
def build_admin(plugin, plugin_dir):
    """
    Creates the plugin's admin.py
    """
    top = open(os.path.join(TEMPLATE_ROOT, 'admin', 'top.txt')).read()
    bottom = open(os.path.join(TEMPLATE_ROOT, 'admin', 'bottom.txt')).read()
    document = open(os.path.join(plugin_dir, 'admin.py'), 'w')
    document.write(render_to_plugin(top, plugin))
    for field in plugin.fields.all():
        document.write("                '%s',\n" % field.name)
    document.write(render_to_plugin(bottom, plugin))
    document.close()
    
def build_the_rest(plugin, plugin_dir):
    """
    Creates the rest of the files for the plugin
    """
    
    managers_txt = open(os.path.join(TEMPLATE_ROOT, 'managers.txt')).read()
    managers = open(os.path.join(plugin_dir, 'managers.py'), 'w')
    managers.write(render_to_plugin(managers_txt, plugin))
    managers.close()
    
    urls_txt = open(os.path.join(TEMPLATE_ROOT, 'urls.txt')).read()
    urls = open(os.path.join(plugin_dir, 'urls.py'), 'w')
    urls.write(render_to_plugin(urls_txt, plugin))
    urls.close()
    
    app_registry_txt = open(os.path.join(TEMPLATE_ROOT, 'app_registry.txt')).read()
    app_registry = open(os.path.join(plugin_dir, 'app_registry.py'), 'w')
    app_registry.write(render_to_plugin(app_registry_txt, plugin))
    app_registry.close()
    
    views_txt = open(os.path.join(TEMPLATE_ROOT, 'views.txt')).read()
    views = open(os.path.join(plugin_dir, 'views.py'), 'w')
    views.write(render_to_plugin(views_txt, plugin))
    views.close()
    
    feeds_txt = open(os.path.join(TEMPLATE_ROOT, 'feeds.txt')).read()
    feeds = open(os.path.join(plugin_dir, 'feeds.py'), 'w')
    feeds.write(render_to_plugin(feeds_txt, plugin))
    feeds.close()
