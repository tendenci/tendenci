from django.contrib import messages
from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson as json
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.defaultfilters import date as date_filter
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.views.decorators.csrf import csrf_exempt

from perms.utils import is_admin
from site_settings.utils import get_setting
from event_logs.models import EventLog
from memberships.models import Membership

from events.models import Event
from events.utils import email_admins
from events.registration.constants import REG_CLOSED, REG_FULL, REG_OPEN
from events.registration.utils import get_available_pricings, reg_status
from events.registration.utils import process_registration, send_registrant_email
from events.registration.forms import RegistrantForm, RegistrationForm
from events.registration.formsets import RegistrantBaseFormSet


@csrf_exempt
def ajax_pricing(request, event_id, template_name="events/registration/pricing.html"):
    """
    Ajax query for pricing info.
    The parameters are email and memberid.
    Both are not unique to a user but are assumed to be unique.
    On cases that there are multiple matches,
    the first match will be the basis of the pricing list
    """
    event = get_object_or_404(Event, pk=event_id)
    
    if not get_setting('module', 'events', 'anonymousmemberpricing'):
        raise Http404
    
    memberid = request.GET.get('memberid', None)
    email = request.GET.get('email', None)
    
    user = AnonymousUser()
    allow_memberid = get_setting('module', 'events', 'memberidpricing')
    if memberid and allow_memberid:# memberid takes priority over email
        membership = Membership.objects.filter(member_number=memberid)
        if membership:
            user = membership[0].user
    elif email:
        user = User.objects.filter(email=email)
        if user:
            user = user[0]
    
    pricings = get_available_pricings(event, user)
    
    pricing_list = []
    for pricing in pricings:
        pricing_list.append({
            'title':pricing.title,
            'quantity':pricing.quantity,
            'price':str(pricing.price),
            'pk':pricing.pk,
        })
    
    data = json.dumps(pricing_list)
    return HttpResponse(data, mimetype="text/plain")

def multi_register(request, event_id, template_name="events/registration/multi_register.html"):
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
    
    # redirect to default registration if anonymousmemberpricing not enabled
    if not get_setting('module', 'events', 'anonymousmemberpricing'):
        return redirect('event.multi_register')
    
    event = get_object_or_404(Event, pk=event_id)
    
    # check if event allows registration
    if (not event.registration_configuration and event.registration_configuration.enabled):
        raise Http404
    
    # check if it is still open, always open for admin users
    if not is_admin(request.user):
        status = reg_status(event, request.user)
        if status == REG_FULL:
            messages.add_message(request, messages.ERROR, _('Registration is full.'))
            return redirect('event', event.pk)
        elif status == REG_CLOSED:
            messages.add_message(request, messages.ERROR, _('Registration is closed.'))
            return redirect('event', event.pk)
    
    user = AnonymousUser()
    # get available pricings
    default_pricings = get_available_pricings(event, user)
    event_pricings = event.registration_configuration.regconfpricing_set.all()
    
    # start the form set factory    
    RegistrantFormSet = formset_factory(
        RegistrantForm,
        formset=RegistrantBaseFormSet,
        can_delete=True,
        extra=0,
    )
    
    if request.method == "POST":
        # process the submitted forms
        reg_formset = RegistrantFormSet(request.POST,
                            prefix='registrant',
                            event = event,
                            extra_params={
                                'pricings':event_pricings,
                            })
        reg_form = RegistrationForm(event, request.user, request.POST,
                            reg_count = len(reg_formset.forms))
        # validate the form and formset
        if False not in (reg_form.is_valid(), reg_formset.is_valid()):
            
            # process the registration
            # this will create the registrants and apply the discount
            reg8n = process_registration(reg_form, reg_formset)
            
            self_reg8n = get_setting('module', 'users', 'selfregistration')
            is_credit_card_payment = (reg8n.payment_method and 
                (reg8n.payment_method.machine_name).lower() == 'credit-card'
                and reg8n.amount_paid > 0)
            
            if is_credit_card_payment: # online payment
                # email the admins as well
                email_admins(event, reg8n.amount_paid, self_reg8n, reg8n)
                # get invoice; redirect to online pay
                return redirect('payments.views.pay_online',
                    reg8n.invoice.id, reg8n.invoice.guid)
            else:
                # offline payment
                # email the registrant
                send_registrant_email(reg8n, self_reg8n)
                # email the admins as well
                email_admins(event, reg8n.amount_paid, self_reg8n, reg8n)
                
            # log an event
            log_defaults = {
                'event_id' : 431000,
                'event_data': '%s (%d) added by %s' % (event._meta.object_name, event.pk, request.user),
                'description': '%s registered for event %s' % (request.user, event.get_absolute_url()),
                'user': request.user,
                'request': request,
                'instance': event,
            }
            EventLog.objects.log(**log_defaults)
            
            # redirect to confirmation
            return redirect('event.registration_confirmation', event_id, reg8n.registrant.hash)
    else:
        # intialize empty forms
        reg_formset = RegistrantFormSet(
                            prefix='registrant',
                            event = event,
                            extra_params={
                                'pricings':event_pricings
                            })
        reg_form = RegistrationForm(event, request.user)
    
    sets = reg_formset.get_sets()
    
    return render_to_response(template_name, {
            'event':event,
            'reg_form':reg_form,
            'registrant': reg_formset,
            'sets': sets,
            'pricings':default_pricings,
            'allow_memberid_pricing':get_setting('module', 'events', 'memberidpricing'),
            }, context_instance=RequestContext(request))
