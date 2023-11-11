from django.template import Library

register = Library()

@register.filter
def is_rep(corp_profile, user):
    if not hasattr(corp_profile, 'is_rep'):
        return None
    return corp_profile.is_rep(user)