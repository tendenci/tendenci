from warnings import warn
from django import template
from .static import do_static as _do_static

register = template.Library()

@register.tag('static')
def do_static(parser, token):
    template = parser.origin.name
    theme = getattr(parser.origin, 'theme', None)
    theme_str = ('theme "%s"'%(theme) if theme else 'an installed Django app')
    warn('{%% load staticfiles %%} in template "%s" in %s is deprecated, use {%% load static %%} instead'%(template, theme_str), DeprecationWarning)
    return _do_static(parser, token)
