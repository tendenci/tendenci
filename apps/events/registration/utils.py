from datetime import datetime

from perms.utils import is_admin, is_member
from site_settings.utils import get_setting

from events.constants import REG_CLOSED, REG_FULL, REG_OPEN
from events.utils import get_event_spots_taken
from events.models import Event, RegConfPricing

def reg_status(event):
    """
    Determines if a registration is open, closed or full.
    """
    
    # check available spots left
    limit = event.registration_configuration.limit
    spots_taken = 0
    if limit > 0: # 0 is no limit
        spots_taken = get_event_spots_taken(event)
        if spots_taken >= limit:
            return 'FULL'
    
    # check if pricings are still open
    pricings = get_available_pricings(event)
    if not pricings:
        return 'CLOSED'
        
    return 'OPEN'

def get_available_pricings(event, user):
    """
    Returns the available pricings of an event for a given user.
    """
    pricings = RegConfPricing.objects.filter(
        reg_conf=event.registration_configuration,
        start_dt__lte=datetime.now(),
        end_dt__lt=datetime.now(),
        status=True,
    )
    
    if is_admin(user):
        # return all if admin is user
        return pricings
    
    anonymousmemberpricing = get_setting('module', 'events', 'anonymousmemberpricing')
    
    if not anonymousmemberpricing:
        if not user.is_authenticated():
            # public pricings only
            pricings = pricings.filter(allow_anonymous=True)
        else:
            exclude_list = []
            # user permitted pricings
            for price in pricings:
                # just to be sure...
                if price.allow_anonymous:
                    continue
                
                # Members allowed
                if price.allow_member and is_member(user):
                    continue
                
                # Group members allowed
                if price.group and price.group.is_member(user):
                    continue
                
                # user failed all permission checks
                exclude_list.append(price.pk)
            # exclude pricings user failed permission checks with
            pricings = pricings.exclude(pk__in=exclude_list)
    
    # return the QUERYSET
    return pricings
