from datetime import datetime

from django.template import Library, TemplateSyntaxError, Variable

from base.template_tags import ListNode, parse_tag_kwargs
from stories.models import Story

register = Library()


@register.inclusion_tag("stories/options.html", takes_context=True)
def stories_options(context, user, story):
    context.update({
        "opt_object": story,
        "user": user,
    })
    return context


@register.inclusion_tag("stories/nav.html", takes_context=True)
def stories_nav(context, user, story=None):
    context.update({
        "nav_object": story,
        "user": user,
    })
    return context


@register.inclusion_tag("stories/search-form.html", takes_context=True)
def stories_search(context):
    return context


class ListStoriesNode(ListNode):
    model = Story


@register.tag
def list_stories(parser, token):
    """
    Example:

    {% list_stories as stories user=user limit=3 %}
    {% for story in stories %}
        {{ story.title }}
    {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires more than 3" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-start_dt'

    return ListStoriesNode(context_var, *args, **kwargs)
