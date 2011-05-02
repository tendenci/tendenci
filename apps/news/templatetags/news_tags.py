from django.template import Node, Library, TemplateSyntaxError, Variable

from base.template_tags import ListNode, parse_tag_kwargs
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
        "nav_object": news,
        "user": user
    })
    return context


@register.inclusion_tag("news/search-form.html", takes_context=True)
def news_search(context):
    return context


class ListNewsNode(ListNode):
    model = News


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

    if len(bits) < 3:
        message = "'%s' tag requires more than 3" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-release_dt'

    return ListNewsNode(context_var, *args, **kwargs)
