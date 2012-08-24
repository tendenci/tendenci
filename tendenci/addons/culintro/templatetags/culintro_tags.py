from django.template import Node, Library, TemplateSyntaxError, Variable

from culintro.models import CulintroJob
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListCulintroJobNode(ListNode):
    model = CulintroJob
    perms = 'culintrojobs.view_project'


@register.inclusion_tag("culintro/nav.html", takes_context=True)
def culintro_nav(context, user, job=None):
    context.update({
        'nav_object': job,
        "user": user
    })
    return context
    
@register.tag
def list_culintrojobs(parser, token):
    """
    Example:

    {% list_culintrojobs as culintrojobs_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for culintrojob in culintrojobs %}
        {{ culintrojob.something }}
    {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires more than 2" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return ListCulintroJobNode(context_var, *args, **kwargs)

@register.inclusion_tag("culintro/search-form.html", takes_context=True)
def culintrojob_search(context):
    return context
