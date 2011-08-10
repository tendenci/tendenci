from django.template import TemplateSyntaxError, TemplateDoesNotExist
from django.template import Library
from django.conf import settings
from django.template.loader import get_template
from django.template.loader_tags import ExtendsNode, IncludeNode, ConstantIncludeNode

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
            print e
            template = get_template(parent)
        return template
        
class ThemeIncludeNone(IncludeNode):
    def render(self, context):
        try:
            template_name = self.template_name.resolve(context)
            theme = context['THEME']
            try:
                t = get_template("%s/templates/%s"%(theme,template_name))
            except TemplateDoesNotExist:
                t = get_template(template_name)
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

    Example::

        {% include "foo/some_include" %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("%r tag takes one argument: the name of the template to be included" % bits[0])
    path = bits[1]
    if path[0] in ('"', "'") and path[-1] == path[0]:
        return ConstantIncludeNode(path[1:-1])
    return ThemeIncludeNode(bits[1])

register.tag('theme_extends', theme_extends)
register.tag('theme_include', theme_include)
