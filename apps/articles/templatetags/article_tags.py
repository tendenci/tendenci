from django.template import Library, TemplateSyntaxError, Variable

from base.template_tags import ListNode, parse_tag_kwargs
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
        "nav_object": article,
        "user": user
    })
    return context


@register.inclusion_tag("articles/search-form.html", takes_context=True)
def article_search(context):
    return context


class ListArticlesNode(ListNode):
    model = Article


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

    if len(bits) < 3:
        message = "'%s' tag requires more than 3" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-release_dt'

    return ListArticlesNode(context_var, *args, **kwargs)
