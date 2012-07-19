from django.template import Library

register = Library()

@register.filter
def allow_edit_by(profile, user):
    """
    Check if the profile allows to be edited by the user. Returns True/False.
    """
    return profile.allow_edit_by(user)
    