from django.template import Library


register = Library()


@register.inclusion_tag("profiles/search-result.html", takes_context=True)
def profile_result(context, profile):
    context.update({
        'profile': profile,
    })
    return context

@register.inclusion_tag("social_services/top_nav_items.html", takes_context=True)
def social_service_current_app(context, user, social_service=None):
    context.update({
        'app_object': social_service,
        "user": user
    })
    return context
