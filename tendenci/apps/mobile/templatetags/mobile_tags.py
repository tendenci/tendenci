from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import TemplateSyntaxError, Variable
from django.utils.translation import ugettext_lazy as _

register = template.Library()

class MobileLinkNode(template.Node):
    def __init__(self, redirect_url, link_name):
        self.redirect_url = redirect_url
        self.link_name = link_name

    def render(self, context):
        try:
            redirect_url = Variable(self.redirect_url)
            redirect_url = redirect_url.resolve(context)
        except:
            redirect_url = self.redirect_url

        return "<a href='%s?next=%s'>%s</a>" % (
            reverse('toggle_mobile_mode'),
            redirect_url,
            self.link_name)

@register.tag(name="toggle_mobile_link")
def toggle_mobile_link(parser, token):
    """
    {% toggle_mobile_link request.get_full_path "See mobile" %}
    """

    bits = token.split_contents()

    if len(bits) > 3:
        message = "'%s' tag requires exactly 2 arguments" % bits[0]
        raise TemplateSyntaxError(_(message))

    return MobileLinkNode(bits[1], bits[2][1:-1])
