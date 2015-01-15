from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.template import Library, TemplateSyntaxError

from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs
from tendenci.apps.articles.models import Article


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


@register.inclusion_tag("articles/top_nav_items.html", takes_context=True)
def article_current_app(context, user, article=None):
    context.update({
        "app_object": article,
        "user": user
    })
    return context


class ListArticlesNode(ListNode):
    model = Article
    perms = 'articles.view_article'

    def custom_model_filter(self, items, user):
        """
        Filters out articles that aren't yet released.
        """
        now = datetime.now().replace(second=0, microsecond=0)
        items = items.filter(release_dt_local__lte=now)
        return items


@register.tag
def list_articles(parser, token):
    """
    Used to pull a list of :model:`articles.Article` items.

    Usage::

        {% list_articles as [varname] [options] %}

    Be sure the [varname] has a specific name like ``articles_sidebar`` or
    ``articles_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``tags="cool"``. Options include:

        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: Newest Release Date**
        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**
        ``query``
           The text to search for items. Will not affect order.
        ``tags``
           The tags required on items to be included.
        ``random``
           Use this with a value of true to randomize the items included.

    Example::

        {% list_articles as articles_list limit=5 tags="cool" %}
        {% for article in articles_list %}
            {{ article.headline }}
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

    if 'order' not in kwargs:
        kwargs['order'] = '-release_dt'

    return ListArticlesNode(context_var, *args, **kwargs)
