from django.template import Node, Library, TemplateSyntaxError, Variable
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

class ListStoriesNode(Node):
    
    def __init__(self, context_var, *args, **kwargs):

        self.limit = 3
        self.user = None
        self.tags = []
        self.q = []
        self.context_var = context_var

        if "limit" in kwargs:
            self.limit = Variable(kwargs["limit"])
        if "user" in kwargs:
            self.user = Variable(kwargs["user"])
        if "tags" in kwargs:
            self.tags = kwargs["tags"]
        if "q" in kwargs:
            self.q = kwargs["q"]

    def render(self, context):
        query = ''

        if self.user:
            self.user = self.user.resolve(context)

        if hasattr(self.limit, "resolve"):
            self.limit = self.limit.resolve(context)

        for tag in self.tags:
            tag = tag.strip()
            query = '%s "tag:%s"' % (query, tag)

        for q_item in self.q:
            q_item = q_item.strip()
            query = '%s "%s"' % (query, q_item)

        stories = Story.objects.search(user=self.user, query=query)
        stories = stories.order_by('start_dt')

        stories = [story.object for story in stories[:self.limit]]
        context[self.context_var] = stories
        return ""

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

    for bit in bits:
        if "limit=" in bit:
            kwargs["limit"] = bit.split("=")[1]
        if "user=" in bit:
            kwargs["user"] = bit.split("=")[1]
        if "tags=" in bit:
            kwargs["tags"] = bit.split("=")[1].replace('"','').split(',')
        if "q=" in bit:
            kwargs["q"] = bit.split("=")[1].replace('"','').split(',')

    if len(bits) < 3:
        message = "'%s' tag requires more than 3" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as" % bits[0]
        raise TemplateSyntaxError(message)

    return ListStoriesNode(context_var, *args, **kwargs)