from django.template import Library, TemplateSyntaxError

from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs
from tendenci.apps.speakers.models import Speaker

register = Library()

@register.inclusion_tag("speakers/top_nav_items.html", takes_context=True)
def speaker_current_app(context, user, speaker=None):
    context.update({
        "app_object": speaker,
        "user": user
    })
    return context


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
    perms = 'speakers.view_speaker'


@register.tag
def list_speakers(parser, token):
    """
    Used to pull a list of :model:`speakers.Speaker` items.

    Usage::

        {% list_speakers as [varname] [options] %}

    Be sure the [varname] has a specific name like ``speakers_sidebar`` or
    ``speakers_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``tags="cool"``. Options include:

        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: Newest Added**
        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**
        ``query``
           The text to search for items. Will not affect order.
        ``tags``
           The tags required on items to be included.
        ``random``
           Use this with a value of true to randomize the items included.

    Example::

        {% list_speakers as speakers_list limit=5 tags="cool" %}
        {% for speaker in speakers_list %}
            {{ speaker.name }}
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
