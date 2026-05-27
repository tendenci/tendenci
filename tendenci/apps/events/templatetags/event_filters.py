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

@register.filter
def is_registrant(event, user):
    """
    Check if this user is a registrant of this event.
    """
    if hasattr(user, 'registrant_set'):
        return user.registrant_set.filter(
            registration__event=event, cancel_dt__isnull=True).exists()
    return False


@register.filter
def can_register_by(pricing, user):
    """
    Check if perms set on this pricing allows it to be registered by the user.
    """
    return pricing.can_register_by(user)


@register.filter
def event_speakers(event, position=None):
    """
    Get event speakers with certain position.
    """
    if position is not None:
        try:
            position = int(position)
        except ValueError:
            position = None
    if position is not None:
        return event.speaker_set.filter(position=position)   
    return event.speaker_set.all()

@register.filter
def show_cert_second_page(sub_events_credits):
    """
    Check if the second page should show for the cert.
    Example of sub_events_credits:
                    {'Aug 6, 2025': [{'alternate_ceu': '',
                    'credits': Decimal('3.0'),
                    'event_code': '1234',
                    'irs_credits': Decimal('2.0'),
                    'title': 'Testing Webcast'}]}
    """
    if sub_events_credits and isinstance(sub_events_credits, dict):
        num_items = len(sub_events_credits)
        if num_items > 1:
            return True
        for k, v_list in sub_events_credits.items():
            if len(v_list) > 1:
                return True
            elif len(v_list) == 1:
                v = v_list[0]
                if 'irs_credits' in v and v['irs_credits'] > 0:
                    return True
    return False
