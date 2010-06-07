from django.template import Library

register = Library()

@register.inclusion_tag("profiles/nav.html")
def users_nav(user_current, user_this):
    if user_this:
        try:
            profile_this = user_this.get_profile()
        except:
            profile_this = None
    else:
        profile_this = None
    
    return {"user":user_current, "user_this": user_this, "profile":profile_this}

@register.inclusion_tag("profiles/options.html")
def users_options(user_current, user_this):
    if user_this:
        try:
            profile_this = user_this.get_profile()
        except:
            profile_this = None
    else:
        profile_this = None
    return {"user":user_current, "user_this": user_this, "profile":profile_this}
