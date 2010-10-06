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

        articles = Article.objects.search(user=self.user)
        articles = [article.object for article in articles[:self.limit]]
        context[self.context_var] = articles
        return ""

@register.tag
def list_articles(parser, token):
    """
    Example:
        {% list_articles as articles [user=user limit=3] %}
        {% for article in articles %}
            {{ article.headline }}
        {% endfor %}

    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    print bits

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

    return ListArticlesNode(context_var, *args, **kwargs)

