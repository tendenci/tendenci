from django.template import Library, TemplateSyntaxError, Variable

from base.template_tags import ListNode, parse_tag_kwargs
from speakers.models import Speaker

register = Library()


@register.inclusion_tag("speakers/options.html", takes_context=True)
def speaker_options(context, user, speaker):
    context.update({
        "opt_object": speaker,
        "user": user
    })
    return context


@register.inclusion_tag("speakers/search-form.html", takes_context=True)
def speaker_search(context):
    return context


class ListSpeakerNode(ListNode):
    model = Speaker


@register.tag
def list_speakers(parser, token):
    """
    Example:

    {% list_speakers as the_speakers user=user limit=3 %}
    {% for speaker_member in the_speakers %}
        {{ speaker_member.name }}
    {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires at least 2 parameters" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return ListSpeakerNode(context_var, *args, **kwargs)
