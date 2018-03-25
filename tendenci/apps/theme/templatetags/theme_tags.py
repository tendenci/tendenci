from builtins import str
import os

from django.template import TemplateSyntaxError, VariableDoesNotExist
from django.template import Library, Variable
from django.template.loader_tags import do_extends, do_include, IncludeNode
from django.contrib.auth.models import AnonymousUser, User
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.boxes.models import Box
from tendenci.apps.perms.utils import get_query_filters
from tendenci.apps.site_settings.models import Setting
from tendenci.apps.site_settings.forms import build_settings_form


register = Library()


# Backward compatibility for old themes
def theme_extends(*args, **kwargs):
    node = do_extends(*args, **kwargs)
    node.must_be_first = False
    return node
register.tag('theme_extends', theme_extends)
register.tag('theme_include', do_include)


class SpaceIncludeNode(IncludeNode):
    def render(self, context):
        context['setting_name'] = str(self.template).replace('MODULE_THEME_', '').lower()
        try:
            setting_value = Variable(self.template).resolve(context)
        except VariableDoesNotExist:
            setting_value = None

        if setting_value:
            # First try to render this as a box
            #user = AnonymousUser()
            #if 'user' in context:
            #    if isinstance(context['user'], User):
            #        user = context['user']
            try:
                # for performance reason, pass AnonymousUser() to reduce the joins of objectpermissions
                # in the meantime, we do want to show public items on homepage
                filters = get_query_filters(AnonymousUser(), 'boxes.view_box')
                box = Box.objects.filter(filters).filter(pk=setting_value)
                context['box'] = box[0]
                template = context.template.engine.get_template('theme_includes/box.html')
                return template.render(context=context)
            except:
                # Otherwise try to render a template
                try:
                    template_name = os.path.join('theme_includes', setting_value)
                    t = context.template.engine.get_template(template_name)
                    return t.render(context=context)
                except:
                    return ''
        else:
            return ''

def space_include(parser, token):
    """
    Loads a box or a template and renders it with the current context.

    Example::

        {% space_include MODULE_THEME_SPACE_1 %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError(_("%r tag takes one argument: the setting whose value should be included" % bits[0]))
    path = bits[1]
    return SpaceIncludeNode(path)

register.tag('space_include', space_include)


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
            t = context.template.engine.get_template("%s/templates/%s" % (theme, template_name))
            return t.render(context=context)
        except:
            return ''

def theme_setting(parser, token):
    """
    Loads a single setting form to edit the setting that is passed in.
    The setting must be of scope 'module' and scope_category 'theme'.
    context['THEME'] is used to specify a selected theme.

    Example::

        {% theme_setting space_1 %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError(_("%r tag takes one argument: the setting to be edited" % bits[0]))
    path = bits[1]
    return ThemeSettingNode(path)

register.tag('theme_setting', theme_setting)
