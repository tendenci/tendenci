from django.template import Node, Library, TemplateSyntaxError, Variable

from trainings.models import Training
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()

@register.inclusion_tag("trainings/search-form.html", takes_context=True)
def training_search(context):
    return context

class ListTrainingsNode(ListNode):
    model = Training


@register.tag
def list_trainings(parser, token):
    """
    Example:

    {% list_trainings as trainings_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for training in trainings %}
        {{ training.something }}
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

    return ListTrainingsNode(context_var, *args, **kwargs)
