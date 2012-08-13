
from django.template import Library

from tendenci.apps.boxes.utils import render_content as rc

register = Library()

@register.filter_function
def render_tags(content, arg=None):
    return rc(content,arg)