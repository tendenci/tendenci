from operator import or_
from functools import reduce

from django.db.models import Q
from django.template import Library, TemplateSyntaxError, Variable, Node

from tendenci.apps.videos.models import Video
from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs

register = Library()


@register.inclusion_tag("videos/top_nav_items.html", takes_context=True)
def video_current_app(context, user, video=None):
    context.update({
        'app_object': video,
        "user": user
    })
    return context


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


class RelatedListNode(Node):

    def __init__(self, video, context_var, *args, **kwargs):
        self.video = video
        self.context_var = context_var
        self.kwargs = kwargs

    def render(self, context):
        limit = 3
        order = u''

        # Check if video exists in context
        try:
            video = Variable(self.video)
            video = video.resolve(context)
        except:
            return ""
        # Check if video is a valid Video instance
        if not isinstance(video, Video):
            return ""

        if 'limit' in self.kwargs:
            try:
                limit = Variable(self.kwargs['limit'])
                limit = limit.resolve(context)
            except:
                limit = self.kwargs['limit']
        limit = int(limit)

        if 'order' in self.kwargs:
            try:
                order = Variable(self.kwargs['order'])
                order = order.resolve(context)
            except:
                order = self.kwargs['order']

        if video.tags:
            tags = video.tags.split(',')
            queries = [Q(tags__icontains=t.strip()) for t in tags]
        else:
            title = video.title.split(' ')
            queries = [Q(title__icontains=t.strip()) for t in title]

        query = reduce(or_, queries)
        items = Video.objects.filter(query).exclude(pk=video.pk)

        # if order is not specified it sorts by relevance
        if order:
            items = items.order_by(order)
        objects = [item for item in items[:limit]]

        context[self.context_var] = objects

        return ""


@register.tag
def related_videos(parser, token):
    """
    Used to pull a list of related videos for a given video.

    Usage::

        {% related_videos video as [varname] [options] %}

    Be sure the [varname] has a specific name like ``videos_sidebar`` or
    ``videos_list``. Options can be used as [option]=[value].

        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: Newest Added**

    Example::

        {% related_videos video as related_list %}
        {% for vid in related_list %}
          {{ vid.title }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    video = bits[1]
    context_var = bits[3]

    if len(bits) < 4:
        message = "'%s' tag requires more than 3 arguments" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[2] != "as":
        message = "'%s' third argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return RelatedListNode(video, context_var, *args, **kwargs)
