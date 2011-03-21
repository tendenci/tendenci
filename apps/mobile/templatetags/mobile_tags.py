from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import TemplateSyntaxError

register = template.Library()

class MobileLinkNode(template.Node):
    def __init__(self, redirect_url, link_name):
        self.redirect_url = redirect_url
        self.link_name = link_name
    
    def render(self, context):
        return "<a href='%s'>%s</a>" % (reverse('toggle_mobile_mode', args=(self.redirect_url,)), self.link_name)

@register.tag(name="toggle_mobile_link")
def toggle_mobile_link(parser, token):
    bits = token.split_contents()
    
    if len(bits) > 3:
        message = "'%s' tag requires exactly 2 arguments" % bits[0]
        raise TemplateSyntaxError(message)
        
    return MobileLinkNode(bits[1][1:-1], bits[2][1:-1])
