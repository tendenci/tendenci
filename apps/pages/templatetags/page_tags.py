from django.template import Node, Library, TemplateSyntaxError, Variable
from pages.models import Page
from datetime import datetime

register = Library()

@register.inclusion_tag("pages/options.html", takes_context=True)
def page_options(context, user, page):
    context.update({
        "opt_object": page,
        "user": user
    })
    return context

@register.inclusion_tag("pages/nav.html", takes_context=True)
def page_nav(context, user, page=None):
    context.update({
        'nav_object': page,
        "user": user
    })
    return context

@register.inclusion_tag("pages/search-form.html", takes_context=True)
def page_search(context):
    return context


class ListPageNode(Node):

    def __init__(self, context_var, *args, **kwargs):

        self.limit = 3
        self.user = None
        self.tags = ''
        self.q = []
        self.context_var = context_var

        if "limit" in kwargs:
            self.limit = Variable(kwargs["limit"])
        if "user" in kwargs:
            self.user = Variable(kwargs["user"])
        if "tags" in kwargs:
            self.tags_string = kwargs['tags']
            self.tags = Variable(kwargs["tags"])
        if "q" in kwargs:
            self.q = kwargs["q"]

    def render(self, context):
        query = ''

        self.tags = self.tags.resolve(context)
        if self.tags:
            self.tags = self.tags.split(',')
        if not self.tags:
            self.tags = self.tags_string.split(',')
            
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

        print query
        pages = Page.objects.search(user=self.user, query=query)
        pages = pages.order_by('create_dt')

        pages = [page.object for page in pages[:self.limit]]
        context[self.context_var] = pages
        return ""

@register.tag
def list_pages(parser, token):
    """
    Example:
        {% list_pages as pages user=user limit=3 %}
        {% for page in pages %}
            {{ page.title }}
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
            kwargs["tags"] = bit.split("=")[1].replace('"','')
        if "q=" in bit:
            kwargs["q"] = bit.split("=")[1].replace('"','').split(',')

    if len(bits) < 3:
        message = "'%s' tag requires at least 2 parameters" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    return ListPageNode(context_var, *args, **kwargs)