from django.template import Node, Library, TemplateSyntaxError, Variable
from articles.models import Article

register = Library()

@register.inclusion_tag("articles/options.html", takes_context=True)
def article_options(context, user, article):
    context.update({
        "opt_object": article,
        "user": user
    })
    return context

@register.inclusion_tag("articles/nav.html", takes_context=True)
def article_nav(context, user, article=None):
    context.update({
        "nav_object" : article,
        "user": user
    })
    return context

@register.inclusion_tag("articles/search-form.html", takes_context=True)
def article_search(context):
    return context

class ListArticlesNode(Node):
    
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


        articles = Article.objects.search(user=self.user, query=query)
        articles = articles.order_by('-release_dt')
        articles = [article.object for article in articles[:self.limit]]
        context[self.context_var] = articles
        return ""

@register.tag
def list_articles(parser, token):
    """
    Example:
        {% list_articles as articles [user=user limit=3 tags=bloop bleep] %}
        {% for article in articles %}
            {{ article.headline }}
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

    return ListArticlesNode(context_var, *args, **kwargs)

