from django.template import Library
register = Library()

@register.filter
def assign_mapped_fields(obj):
    """assign mapped field from custom registration form to registrant"""
    if hasattr(obj, 'custom_reg_form_entry') and obj.custom_reg_form_entry:
        obj.assign_mapped_fields()
    return obj

@register.filter
def discount_used(events):
    for event in events:
        if event.discount_count > 0:
            return True
    return False
