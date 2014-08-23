from django.template import Library, Node, TemplateSyntaxError, Variable
from django.utils.translation import ugettext_lazy as _
#from django.template.loader import get_template

from tendenci.apps.pluginmanager.models import PluginApp

register = Library()


class ListPluginsNode(Node):
    def __init__(self, context_var):
        self.context_var = context_var

    def render(self, context):
        plugins = PluginApp.objects.filter(is_enabled=True)
        plugins = plugins.order_by('title')

        context[self.context_var] = plugins
        return ""


@register.tag
def list_plugins(parser, token):
    """
    Example:
        {% list_plugins as plugins %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()

    if len(bits) < 3:
        message = "'%s' tag requires more than 2" % bits[0]
        raise TemplateSyntaxError(_(message))

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(_(message))

    context_var = bits[2]


    return ListPluginsNode(context_var)
