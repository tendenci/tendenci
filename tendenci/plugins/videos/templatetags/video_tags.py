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
    perms = 'videos.view_video'


@register.tag
def list_videos(parser, token):
    """
    Used to pull a list of :model:`videos.Video` items.

    Usage::

        {% list_videos as [varname] [options] %}

    Be sure the [varname] has a specific name like ``videos_sidebar`` or 
    ``videos_list``. Options can be used as [option]=[value]. Wrap text values
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

        {% list_videos as videos_list limit=5 tags="cool" %}
        {% for video in videos_list %}
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
