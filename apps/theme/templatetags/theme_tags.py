import os
from django.template import TemplateSyntaxError, TemplateDoesNotExist, VariableDoesNotExist
from django.template import Library, Template
from django.conf import settings
from django.template.loader import get_template
from django.template.loader_tags import ExtendsNode, IncludeNode, ConstantIncludeNode

from boxes.models import Box

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
                pass #raise
            return ''

class SpaceIncludeNode(IncludeNode):
    def render(self, context):
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
                template = get_template('boxes/edit-link.html')
                output = '<div id="box-%s" class="boxes">%s %s</div>' % (
                    box.object.pk,
                    box.object.content,
                    template.render(context),
                )
                return output
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
                    return ''
        else:
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
    Example:
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
    Example:
        {% space_include MODULE_THEME_SPACE_1 %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("%r tag takes one argument: the setting to be included" % bits[0])
    path = bits[1]
    return SpaceIncludeNode(bits[1])

register.tag('theme_extends', theme_extends)
register.tag('theme_include', theme_include)
register.tag('space_include', space_include)
