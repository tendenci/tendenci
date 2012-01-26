import os
from django.template import TemplateSyntaxError, TemplateDoesNotExist, VariableDoesNotExist
from django.template import Library, Template, Variable
from django.conf import settings
from django.template.loader import get_template
from django.template.loader_tags import ExtendsNode, IncludeNode, ConstantIncludeNode

from boxes.models import Box
from site_settings.models import Setting
from site_settings.forms import build_settings_form

register = Library()

class ThemeExtendsNode(ExtendsNode):
    must_be_first = False
    
    def get_parent(self, context):
        if self.parent_name_expr:
            self.parent_name = self.parent_name_expr.resolve(context)
        parent = self.parent_name
        if not parent:
            error_msg = "Invalid template name in 'extends' tag: %r." % parent
            if self.parent_name_expr:
                error_msg += " Got this from the '%s' variable." % self.parent_name_expr.token
            raise TemplateSyntaxError(error_msg)
        if hasattr(parent, 'render'):
            return parent # parent is a Template object
        theme = context['THEME']
        try:
            template = get_template("%s/templates/%s"%(theme,parent))
        except TemplateDoesNotExist, e:
            #load the true default template directly to be sure
            #that we are not loading the active theme's template
            template = Template(unicode(file(os.path.join(settings.PROJECT_ROOT, "templates", parent)).read(), "utf-8"))
        return template
        
class ThemeConstantIncludeNode(ConstantIncludeNode):
    def __init__(self, template_path):
        self.template_path = template_path

    def render(self, context):
        theme = context['THEME']
        try:
            try:
                t = get_template("%s/templates/%s" % (theme, self.template_path))
            except TemplateDoesNotExist:
                t = Template(unicode(file(os.path.join(settings.PROJECT_ROOT, "templates", self.template_path)).read(), "utf-8"))
            self.template = t
        except:
            if settings.TEMPLATE_DEBUG:
                raise
            self.template = None
        if self.template:
            return self.template.render(context)
        else:
            return ''
        
class ThemeIncludeNode(IncludeNode):
    def render(self, context):
        try:
            template_name = self.template_name.resolve(context)
            theme = context['THEME']
            try:
                t = get_template("%s/templates/%s"%(theme,template_name))
            except TemplateDoesNotExist:
                #load the true default template directly to be sure
                #that we are not loading the active theme's template
                t = Template(unicode(file(os.path.join(settings.PROJECT_ROOT, "templates", template_name)).read(), "utf-8"))
            return t.render(context)
        except:
            if settings.TEMPLATE_DEBUG:
                raise
            return ''

class SpaceIncludeNode(IncludeNode):
    def render(self, context):
        context['setting_name'] = unicode(self.template_name).replace('MODULE_THEME_','').lower()
        try:
            setting_value = self.template_name.resolve(context)
        except VariableDoesNotExist:
            setting_value = None

        if setting_value:
            # First try to render this as a box
            query = '"pk:%s"' % (setting_value)
            try:
                box = Box.objects.search(query=query).best_match()
                context['box'] = box.object
                template = get_template('theme_includes/box.html')
                return template.render(context)
            except:
                # Otherwise try to render a template
                try:
                    template_name = setting_value
                    theme = context['THEME']
                    try:
                        t = get_template("%s/templates/theme_includes/%s"%(theme,template_name))
                    except TemplateDoesNotExist:
                        #load the true default template directly to be sure
                        #that we are not loading the active theme's template
                        t = Template(unicode(file(os.path.join(settings.PROJECT_ROOT, "templates", "theme_includes", template_name)).read(), "utf-8"))
                    return t.render(context)
                except:
                    if settings.TEMPLATE_DEBUG:
                        raise
                    return ''
        else:
            return ''

class ThemeSettingNode(IncludeNode):
    def __init__(self, setting_name):
        self.setting_name = setting_name

    def render(self, context):
        try:
            setting_name = Variable(self.setting_name)
            setting_name = setting_name.resolve(context)

        except:
            setting_name = self.setting_name
        full_setting_name = ''.join(['module_theme_',setting_name]).upper()
        try:
            setting_value = Variable(full_setting_name)
            setting_value = setting_value.resolve(context)
            setting_value = setting_value.replace('.html','')
        except:
            setting_value = None
        settings_list = Setting.objects.filter(scope='module', scope_category='theme', name=setting_name)
        settings_value_list = Setting.objects.filter(scope='template', scope_category=setting_value)
        context['setting_name'] = setting_name
        context['setting_value'] = setting_value
        context['settings_value_list'] = settings_value_list
        context['scope_category'] = 'theme'
        context['setting_form'] = build_settings_form(context['user'], settings_list)()
        context['setting_value_form'] = build_settings_form(context['user'], settings_value_list)()
        template_name = 'theme_includes/setting_edit_form.html'
        try:
            theme = context['THEME']
            try:
                t = get_template("%s/templates/%s"%(theme,template_name))
            except TemplateDoesNotExist:
                #load the true default template directly to be sure
                #that we are not loading the active theme's template
                t = Template(unicode(file(os.path.join(settings.PROJECT_ROOT, "templates", template_name)).read(), "utf-8"))
            return t.render(context)
        except:
            if settings.TEMPLATE_DEBUG:
                raise
            return ''


def theme_extends(parser, token):
    """
    Signal that this template extends a parent template.

    This tag may be used in two ways: ``{% theme_extends "base" %}`` (with quotes)
    uses the literal value "base" as the name of the parent template to extend,
    or ``{% extends variable %}`` uses the value of ``variable`` as either the
    name of the parent template to extend (if it evaluates to a string) or as
    the parent tempate itelf (if it evaluates to a Template object).
    
    The template rendered by this extends is based on the active theme or
    the theme specified in request.GET.get('theme')
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' takes one argument" % bits[0])
    parent_name, parent_name_expr = None, None
    if bits[1][0] in ('"', "'") and bits[1][-1] == bits[1][0]:
        parent_name = bits[1][1:-1]
    else:
        parent_name_expr = parser.compile_filter(bits[1])
    nodelist = parser.parse()
    if nodelist.get_nodes_by_type(ExtendsNode):
        raise TemplateSyntaxError("'%s' cannot appear more than once in the same template" % bits[0])
    return ThemeExtendsNode(nodelist, parent_name, parent_name_expr)

def theme_include(parser, token):
    """
    Loads a template and renders it with the current context.
    context['THEME'] is used to specify a selected theme for the templates

    Example::

        {% theme_include "foo/some_include" %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("%r tag takes one argument: the name of the template to be included" % bits[0])
    path = bits[1]
    if path[0] in ('"', "'") and path[-1] == path[0]:
        return ThemeConstantIncludeNode(path[1:-1])
    return ThemeIncludeNode(bits[1])

def space_include(parser, token):
    """
    Loads a a box or a template and renders it with the current context.
    context['THEME'] is used to specify a selected theme for the templates

    Example::

        {% space_include MODULE_THEME_SPACE_1 %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("%r tag takes one argument: the setting to be included" % bits[0])
    path = bits[1]
    return SpaceIncludeNode(bits[1])

def theme_setting(parser, token):
    """
    Loads a single setting form to edit the setting that is passed in.
    The setting must be of scope 'module' and scope_category 'theme'.

    Example::

        {% theme_setting space_1 %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("%r tag takes one argument: the setting to be included" % bits[0])
    path = bits[1]
    return ThemeSettingNode(bits[1])

register.tag('theme_extends', theme_extends)
register.tag('theme_include', theme_include)
register.tag('space_include', space_include)
register.tag('theme_setting', theme_setting)

