from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.defaultfilters import date as date_filter
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import Http404
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory

from events.registration.constants import REG_CLOSED, REG_FULL, REG_OPEN
from events.registration.utils import get_available_pricings, reg_is_open
from events.registration.forms import PricingForm, RegistrantForm

try:
    from notification import models as notification
except:
    notification = None   

def multi_register(request, event_id, template_name="events/reg8n/multi_register.html"):
    """
    This view is where a user defines the specifics of his/her registrations.
    A registration set is a set of registrants (one or many) that comply with a specific pricing.
    A pricing defines the maximum number of registrants in a registration set.
    A user can avail multiple registration sets.
    If the site setting anonymousmemberpricing is enabled,
    anonymous users can select non public pricings in their registration sets,
    provided that the first registrant of every registration set's email is validated to be an existing user.
    If the site setting anonymousmemberpricing is disabled,
    anonymous users will not be able to see non public prices.
    """
    event = get_object_or_404(Event, pk=event_id)

    # check if event allows registration
    if (not event.registration_configuration and event.registration_configuration.enabled):
        raise Http404
    
    # check if it is still open
    status = reg_status(event)
    if status == REG_FULL:
        messages.add_message(request, messages.ERROR, _('Registration is full.'))
        return redirect('event', event.pk)
    elif status == REG_CLOSED:
        messages.add_message(request, messages.ERROR, _('Registration is closed.'))
        return redirect('event', event.pk)
    
    # start the form set factory    
    RegistrantFormSet = formset_factory(
        RegistrantForm,
        formset=RegistrantBaseFormSet,
        can_delete=True,
        max_num=price.quantity,
        extra=(price.quantity - 1),
    )
    
    
