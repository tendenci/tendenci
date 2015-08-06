import os
from django.template import TemplateSyntaxError, TemplateDoesNotExist, VariableDoesNotExist
from django.template import Library, Template, Variable
from django.conf import settings
from django.template.base import TextNode
from django.template.loader import get_template
from django.template.loader_tags import (ExtendsNode, IncludeNode,
                                         BlockNode, BlockContext,
                                         BLOCK_CONTEXT_KEY,)
from django.contrib.auth.models import AnonymousUser, User
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.boxes.models import Box
from tendenci.apps.perms.utils import get_query_filters
from tendenci.apps.site_settings.models import Setting
from tendenci.apps.site_settings.forms import build_settings_form
from tendenci.apps.site_settings.utils import get_setting

from tendenci.apps.theme.template_loaders import get_default_template
from tendenci.apps.theme.utils import get_theme_template

register = Library()

class ThemeExtendsNode(ExtendsNode):
    must_be_first = False

    # def __init__(self, nodelist, parent_name, parent_name_expr):
    #     self.parent_name = parent_name
    #     self.parent_name_expr = parent_name_expr
    #     self.nodelist = nodelist
    #     self.blocks = dict([(n.name, n) for n in nodelist.get_nodes_by_type(BlockNode)])

    # def get_parent(self, context):
    #     if self.parent_name_expr:
    #         self.parent_name = self.parent_name_expr.resolve(context)
    #     parent = unicode(self.parent_name)

    #     if not parent:
    #         error_msg = "Invalid template name in 'extends' tag: %r." % parent
    #         if self.parent_name_expr:
    #             error_msg += " Got this from the '%s' variable." % self.parent_name_expr.token
    #         raise TemplateSyntaxError(_(error_msg))
    #     if hasattr(parent, 'render'):
    #         return parent  # parent is a Template object
    #     theme = context.get('THEME', get_setting('module', 'theme_editor', 'theme'))
    #     theme_template = get_theme_template(parent, theme=theme)
    #     try:
    #         template = get_template(theme_template)
    #     except TemplateDoesNotExist:
    #         #to be sure that we not are loading the active theme's template
    #         template = get_default_template(parent)

    #     return template

    def __init__(self, nodelist, parent_name, template_dirs=None):
        self.nodelist = nodelist
        self.parent_name = parent_name
        self.template_dirs = template_dirs
        self.blocks = dict([(n.name, n) for n in nodelist.get_nodes_by_type(BlockNode)])

    def __repr__(self):
        return '<ThemeExtendsNode: theme_extends %s>' % self.parent_name.token

    def get_parent(self, context):
        parent = self.parent_name.resolve(context)
        if not parent:
            error_msg = "Invalid template name in 'extends' tag: %r." % parent
            if self.parent_name.filters or\
                    isinstance(self.parent_name.var, Variable):
                error_msg += " Got this from the '%s' variable." %\
                    self.parent_name.token
            raise TemplateSyntaxError(error_msg)
        if hasattr(parent, 'render'):
            return parent # parent is a Template object

        theme = context.get('THEME', get_setting('module', 'theme_editor', 'theme'))
        theme_template = get_theme_template(parent, theme=theme)
        try:
            template = context.template.engine.get_template(theme_template)
        except TemplateDoesNotExist:
            # to be sure that we are not loadnig the active theme's template
            template = context.template.engine.get_template(parent)

        return template

    def render(self, context):
        compiled_parent = self.get_parent(context)

        if BLOCK_CONTEXT_KEY not in context.render_context:
            context.render_context[BLOCK_CONTEXT_KEY] = BlockContext()
        block_context = context.render_context[BLOCK_CONTEXT_KEY]

        # Add the block nodes from this node to the block context
        block_context.add_blocks(self.blocks)

        # If this block's parent doesn't have an extends node it is the root,
        # and its block nodes also need to be added to the block context.
        for node in compiled_parent.nodelist:
            # The ExtendsNode has to be the first non-text node.
            if not isinstance(node, TextNode):
                if not isinstance(node, ThemeExtendsNode) and not isinstance(node, ExtendsNode):
                    blocks = dict([(n.name, n) for n in
                                   compiled_parent.nodelist.get_nodes_by_type(BlockNode)])
                    block_context.add_blocks(blocks)
                break

        # Call Template._render explicitly so the parser context stays
        # the same.
        return compiled_parent._render(context)


class ThemeConstantIncludeNode(IncludeNode):
    def __init__(self, template_path):
        self.template_path = template_path

    def render(self, context):
        theme = context.get('THEME', get_setting('module', 'theme_editor', 'theme'))
        theme_template = get_theme_template(self.template_path, theme=theme)
        try:
            try:
                t = get_template(theme_template)
            except TemplateDoesNotExist:
                t = get_default_template(self.template_path)
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
            theme = context.get('THEME', get_setting('module', 'theme_editor', 'theme'))
            theme_template = get_theme_template(template_name, theme=theme)
            try:
                t = get_template(theme_template)
            except TemplateDoesNotExist:
                t = get_default_template(template_name)
            return t.render(context)
        except:
            if settings.TEMPLATE_DEBUG:
                raise
            return ''


class SpaceIncludeNode(IncludeNode):
    def render(self, context):
        context['setting_name'] = unicode(self.template).replace('MODULE_THEME_', '').lower()
        try:
            setting_value = Variable(self.template).resolve(context)
        except VariableDoesNotExist:
            setting_value = None

        if setting_value:
            # First try to render this as a box
            user = AnonymousUser()
            if 'user' in context:
                if isinstance(context['user'], User):
                    user = context['user']
            try:
                # for performance reason, pass AnonymousUser() to reduce the joins of objectpermissions
                # in the meantime, we do want to show public items on homepage
                filters = get_query_filters(AnonymousUser(), 'boxes.view_box')
                box = Box.objects.filter(filters).filter(pk=setting_value)
                context['box'] = box[0]
                template = get_template('theme_includes/box.html')
                return template.render(context)
            except:
                # Otherwise try to render a template
                try:
                    template_name = os.path.join('theme_includes', setting_value)
                    theme = context.get('THEME', get_setting('module', 'theme_editor', 'theme'))
                    theme_template = get_theme_template(template_name, theme=theme)
                    try:
                        t = get_template(theme_template)
                    except TemplateDoesNotExist:
                        t = get_default_template(template_name)
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

        # If not a user or not an admin, don't return the form.
        if not isinstance(context['user'], User):
            return ''
        if not context['user'].profile.is_superuser:
            return ''

        try:
            setting_name = Variable(self.setting_name)
            setting_name = setting_name.resolve(context)

        except:
            setting_name = self.setting_name
        full_setting_name = ''.join(['module_theme_', setting_name]).upper()
        try:
            setting_value = Variable(full_setting_name)
            setting_value = setting_value.resolve(context)
            setting_value = setting_value.replace('.html', '')
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
                t = get_template("%s/templates/%s" % (theme, template_name))
            except TemplateDoesNotExist:
                #load the true default template directly to be sure
                #that we are not loading the active theme's template
                t = get_default_template(template_name)
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
    # bits = token.split_contents()
    # if len(bits) != 2:
    #     raise TemplateSyntaxError(_("'%s' takes one argument" % bits[0]))
    # parent_name, parent_name_expr = None, None
    # if bits[1][0] in ('"', "'") and bits[1][-1] == bits[1][0]:
    #     parent_name = bits[1][1:-1]
    # else:
    #     parent_name_expr = parser.compile_filter(bits[1])
    # nodelist = parser.parse()
    # if nodelist.get_nodes_by_type(ExtendsNode):
    #     raise TemplateSyntaxError(_("'%s' cannot appear more than once in the same template" % bits[0]))

    # return ThemeExtendsNode(nodelist, parent_name, parent_name_expr)

    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' takes one argument" % bits[0])
    parent_name = parser.compile_filter(bits[1])
    nodelist = parser.parse()

    if nodelist.get_nodes_by_type(ExtendsNode):
        raise TemplateSyntaxError("'%s' cannot appear more than once in the same template" % bits[0])
    return ThemeExtendsNode(nodelist, parent_name)


def theme_include(parser, token):
    """
    Loads a template and renders it with the current context.
    context['THEME'] is used to specify a selected theme for the templates

    Example::

        {% theme_include "foo/some_include" %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError(_("%r tag takes one argument: the name of the template to be included" % bits[0]))
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
        raise TemplateSyntaxError(_("%r tag takes one argument: the setting to be included" % bits[0]))
    path = bits[1]
    return SpaceIncludeNode(path)


def theme_setting(parser, token):
    """
    Loads a single setting form to edit the setting that is passed in.
    The setting must be of scope 'module' and scope_category 'theme'.

    Example::

        {% theme_setting space_1 %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError(_("%r tag takes one argument: the setting to be included" % bits[0]))
    path = bits[1]
    return ThemeSettingNode(bits[1])

register.tag('theme_extends', theme_extends)
register.tag('theme_include', theme_include)
register.tag('space_include', space_include)
register.tag('theme_setting', theme_setting)
