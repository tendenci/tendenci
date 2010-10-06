from django.template import Node, Library, TemplateSyntaxError, Variable
from news.models import News

register = Library()

@register.inclusion_tag("news/options.html", takes_context=True)
def news_options(context, user, news):
    context.update({
        "opt_object": news,
        "user": user
    })
    return context

@register.inclusion_tag("news/nav.html", takes_context=True)
def news_nav(context, user, news=None):
    context.update({
        "nav_object" : news,
        "user": user
    })
    return context

@register.inclusion_tag("news/search-form.html", takes_context=True)
def news_search(context):
    return context

class ListNewsNode(Node):
    
    def __init__(self, context_var, *args, **kwargs):

        self.limit = 3
        self.user = None

        if "limit" in kwargs:
            self.limit = Variable(kwargs["limit"])

        if "user" in kwargs:
            self.user = Variable(kwargs["user"])

        self.context_var = context_var

    def render(self, context):

        if self.user:
            self.user = self.user.resolve(context)

        if hasattr(self.limit, "resolve"):
            self.limit = self.limit.resolve(context)

        news = News.objects.search(user=self.user)
        news = [news_item.object for news_item in news[:self.limit]]
        context[self.context_var] = news
        return ""

@register.tag
def list_news(parser, token):
    """
    Example:
        {% list_news as news [user=user limit=3] %}
        {% for news_item in news %}
            {{ news_item.headline }}
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

    if len(bits) < 3:
        message = "'%s' tag requires more than 3" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as" % bits[0]
        raise TemplateSyntaxError(message)

    return ListNewsNode(context_var, *args, **kwargs)
