from django.template import Library, TemplateSyntaxError, Variable

from videos.models import Video
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


@register.inclusion_tag("videos/options.html", takes_context=True)
def video_options(context, user, video):
    context.update({
        "opt_object": video,
        "user": user
    })
    return context


class ListVideosNode(ListNode):
    model = Video


@register.tag
def list_videos(parser, token):
    """
    Example:

    {% list_videos as videos [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for video in videos %}
        {{ video.title }}
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

    return ListVideosNode(context_var, *args, **kwargs)
