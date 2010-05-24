from django.template import Library

register = Library()

@register.inclusion_tag("articles/options.html", takes_context=True)
def article_options(context, article, user):
    context.update({
        "article": article,
        "user": user
    })
    return context