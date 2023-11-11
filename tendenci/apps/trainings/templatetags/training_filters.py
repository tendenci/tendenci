from django.template import Library

register = Library()

@register.filter
def get_earned_credits(cert_cat, user):
    if not hasattr(cert_cat, 'get_earned_credits'):
        return None
    return cert_cat.get_earned_credits(user)
