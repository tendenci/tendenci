from builtins import str
import random
from datetime import datetime
from operator import or_, and_
from functools import reduce

from django.contrib.auth.models import AnonymousUser, User
from django.db import models
from django.db.models import Q
from django.template import Library, TemplateSyntaxError, Variable
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from tendenci.apps.stories.models import Story
from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs
from tendenci.apps.perms.utils import get_query_filters


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


@register.inclusion_tag("stories/top_nav_items.html", takes_context=True)
def story_current_app(context, user, story=None):
    context.update({
        "app_object": story,
        "user": user
    })
    return context


@register.simple_tag
def story_expiration(obj):
    t = '<span class="t-expires t-expires-%s">%s</span>'

    if obj.expires:
        if obj.end_dt < datetime.now():
            value = t % ('inactive', ("Expired on %s" % obj.end_dt.strftime("%m/%d/%Y at %I:%M %p")))
        else:
            if obj.start_dt > datetime.now():
                value = t % ('inactive',("Starts on %s" % obj.start_dt.strftime("%m/%d/%Y at %I:%M %p")))
            else:
                value = t % ('active', ("Expires on %s" % obj.end_dt.strftime("%m/%d/%Y at %I:%M %p")))
    else:
        value = t % ('active', "Never Expires")

    return mark_safe(value)


class ListStoriesNode(ListNode):
    model = Story
    perms = 'stories.view_story'

    def __init__(self, context_var, *args, **kwargs):
        self.context_var = context_var
        self.kwargs = kwargs

        if not self.model:
            raise AttributeError(_('Model attribute must be set'))
        if not issubclass(self.model, models.Model):
            raise AttributeError(_('Model attribute must derive from Model'))
        if not hasattr(self.model.objects, 'search'):
            raise AttributeError(_('Model.objects does not have a search method'))

    def render(self, context):
        tags = u''
        query = u''
        user = AnonymousUser()
        limit = 3
        order = u''
        randomize = False
        group = u''

        if 'random' in self.kwargs:
            randomize = bool(self.kwargs['random'])

        if 'tags' in self.kwargs:
            try:
                tags = Variable(self.kwargs['tags'])
                tags = str(tags.resolve(context))
            except:
                tags = self.kwargs['tags']

            tags = tags.replace('"', '')
            tags = [t.strip() for t in tags.split(',')]

        if 'user' in self.kwargs:
            try:
                user = Variable(self.kwargs['user'])
                user = user.resolve(context)
            except:
                user = self.kwargs['user']
        else:
            # check the context for an already existing user
            if 'user' in context:
                user = context['user']

        if 'limit' in self.kwargs:
            try:
                limit = Variable(self.kwargs['limit'])
                limit = limit.resolve(context)
            except:
                limit = self.kwargs['limit']

        limit = int(limit)

        if 'query' in self.kwargs:
            try:
                query = Variable(self.kwargs['query'])
                query = query.resolve(context)
            except:
                query = self.kwargs['query']  # context string

        if 'order' in self.kwargs:
            try:
                order = Variable(self.kwargs['order'])
                order = order.resolve(context)
            except:
                order = self.kwargs['order']

        if 'group' in self.kwargs:
            try:
                group = Variable(self.kwargs['group'])
                group = str(group.resolve(context))
            except:
                group = self.kwargs['group']

            try:
                group = int(group)
            except:
                group = None

        filters = get_query_filters(user, self.perms)
        items = self.model.objects.filter(filters)
        if isinstance(user, User) and user.is_authenticated:
            if not user.profile.is_superuser:
                items = items.distinct()

        if tags:  # tags is a comma delimited list
            # this is fast; but has one hole
            # it finds words inside of other words
            # e.g. "prev" is within "prevent"
            tag_queries = [Q(tags__iexact=t.strip()) for t in tags]
            tag_queries += [Q(tags__istartswith=t.strip()+",") for t in tags]
            tag_queries += [Q(tags__iendswith=", "+t.strip()) for t in tags]
            tag_queries += [Q(tags__iendswith=","+t.strip()) for t in tags]
            tag_queries += [Q(tags__icontains=", "+t.strip()+",") for t in tags]
            tag_queries += [Q(tags__icontains=","+t.strip()+",") for t in tags]
            tag_query = reduce(or_, tag_queries)
            items = items.filter(tag_query)

        if group:
            items = items.filter(group=group)

        objects = []

        # Removed seconds and microseconds so we can cache the query better
        now = datetime.now().replace(second=0, microsecond=0)

        # Custom filter for stories
        date_query = reduce(or_, [Q(end_dt__gte=now), Q(expires=False)])
        date_query = reduce(and_, [Q(start_dt__lte=now), date_query])
        items = items.filter(date_query)

        if order:
            items = items.order_by(order)
        else:
            items = items.order_by('-position', '-start_dt')

        # if order is not specified it sorts by relevance
        if randomize:
            items = list(items)
            objects = random.sample(items, min(len(items), limit))
        else:
            objects = items[:limit]

        context[self.context_var] = objects

        return ""


@register.tag
def list_stories(parser, token):
    """
    Used to pull a list of :model:`stories.Story` items.

    Usage::

        {% list_stories as [varname] [options] %}

    Be sure the [varname] has a specific name like ``stories_sidebar`` or
    ``stories_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``tags="cool"``. Options include:

        ``limit``
           The number of stories that are shown. **Default: 3**
        ``order``
           The order of the stories. **Default: Order in Admin**
        ``user``
           Specify a user to only show public stories to all. **Default: Viewing user**
        ``query``
           The text to search for stories. Will not affect order.
        ``tags``
           The tags required on stories to be included.
        ``group``
           The group id of stories to be included.
        ``random``
           Use this with a value of true to randomize the stories included.

    Example::

        {% list_stories as stories_list limit=5 tags="cool" %}
        {% for story in stories_list %}
            {{ story.title }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires more than 3" % bits[0]
        raise TemplateSyntaxError(_(message))

    if bits[1] != "as":
        message = "'%s' second argument must be 'as" % bits[0]
        raise TemplateSyntaxError(_(message))

    kwargs = parse_tag_kwargs(bits)

    return ListStoriesNode(context_var, *args, **kwargs)
