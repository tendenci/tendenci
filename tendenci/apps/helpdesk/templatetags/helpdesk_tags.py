from django.template import Library
register = Library()

@register.inclusion_tag("helpdesk/top_nav_items.html", takes_context=True)
def helpdesk_current_app(context, user):
    context.update({
        "user": user,
    })
    return context
