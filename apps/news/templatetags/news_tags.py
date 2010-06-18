from django.template import Library

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