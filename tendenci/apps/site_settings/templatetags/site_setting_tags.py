from django.template import Library, Node

from tendenci.apps.site_settings.utils import get_setting as gs


register = Library()


class GetSettingNode(Node):
    def __init__(self, scope, scope_category, name, context_var=None):
        self.scope = scope
        self.scope_category = scope_category
        self.name = name
        self.context_var = context_var
    def render(self, context):
        value = gs(self.scope, self.scope_category, self.name)
        context[self.context_var] = value
        return ''


@register.tag
def get_setting(parser, token):
    """
        Gets and sets the value of a setting
        {% get_setting scope scope_category name as context}
    """
    bits  = token.split_contents()

    try: scope = bits[1]
    except: scope = None

    try: scope_category = bits[2]
    except: scope_category = None

    try: name = bits[3]
    except: name = None

    try: context_var = bits[5]
    except: context_var = None

    return GetSettingNode(scope, scope_category, name, context_var=context_var)


@register.inclusion_tag("site_settings/options.html", takes_context=True)
def settings_options(context, user, setting):
    context.update({
        "setting": setting,
        "user": user
    })
    return context


@register.inclusion_tag("site_settings/nav.html", takes_context=True)
def settings_nav(context, user, scope_category=None):
    context.update({
        "user": user,
        "scope_category": scope_category
    })
    return context


@register.inclusion_tag("site_settings/top_nav_items.html", takes_context=True)
def settings_current_app(context, user, scope_category=None):
    context.update({
        "user": user,
        "app_object": scope_category
    })
    return context
