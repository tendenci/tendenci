from django.template.loader import get_template
from .models import AllowedConnection


def get_allowed_affiliate_types(corp_type):
    """
    Given a corp_type, return a list of allowed affiliate types.
    """
    allowed_affiliate_types = []
    for ac in AllowedConnection.objects.filter(corp_type=corp_type):
        allowed_affiliate_types += list(ac.member_types.all())
        
    return allowed_affiliate_types
 
 
def types_in_allowed_connection(corp_type, member_type):
    """
    Check if member_type is in the allowed connections to corp_type.
    """
    if corp_type and member_type:
        if AllowedConnection.objects.filter(
            corp_type=corp_type, member_types__in=[member_type]).exists():
            return True

    return False

def get_content_from_template(template_name, context):
    template = get_template(template_name)
    return template.render(context=context)
    
   