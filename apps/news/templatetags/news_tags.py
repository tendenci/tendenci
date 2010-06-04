from django.template import Library

register = Library()

@register.inclusion_tag("news/options.html", takes_context=True)
def news_options(context, user, news):
    context.update({
        "news": news,
        "user": user
    })
    return context

@register.inclusion_tag("news/nav.html", takes_context=True)
def news_nav(context, user):
    context.update({
        "user": user
    })
    return context