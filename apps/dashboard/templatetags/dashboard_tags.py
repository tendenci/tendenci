from django.template import Library
register = Library()

@register.inclusion_tag("dashboard/nav.html", takes_context=True)
def dashboard_nav(context, user):
    context.update({
        "user": user
    })
    return context