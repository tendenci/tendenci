from django.template import Library

register = Library()

@register.inclusion_tag("profiles/nav.html", takes_context=True)
def users_nav(context, user_current, user_this):
    if user_this:
        try:
            profile_this = user_this.get_profile()
        except:
            profile_this = None
    else:
        profile_this = None
    context.update({
        "user_current":user_current,
        "user_this": user_this,
        "nav_object": profile_this,
        "profile":profile_this
    })

    return context

@register.inclusion_tag("profiles/options.html", takes_context=True)
def users_options(context, user_current, user_this):
    if user_this:
        try:
            profile_this = user_this.get_profile()
        except:
            profile_this = None
    else:
        profile_this = None
    context.update({
        "user_current":user_current,
        "user_this": user_this,
        "profile":profile_this
    })
    return context

@register.inclusion_tag("profiles/search-form.html", takes_context=True)
def profile_search(context):
    return context

