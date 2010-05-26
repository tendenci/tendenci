from django.template import Library

register = Library()

@register.inclusion_tag("articles/options.html", takes_context=True)
def article_options(context, user, article):
    context.update({
        "article": article,
        "user": user
    })
    return context

@register.inclusion_tag("articles/nav.html", takes_context=True)
def article_nav(context, user):
    context.update({
        "user": user
    })
    return context