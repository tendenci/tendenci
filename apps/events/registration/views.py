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

from events.models import Event, RegConfPricing, Registrant
from events.utils import email_admins
from events.registration.constants import REG_CLOSED, REG_FULL, REG_OPEN
from events.registration.utils import get_available_pricings, reg_status
from events.registration.utils import can_use_pricing, get_active_pricings 
from events.registration.utils import process_registration, send_registrant_email
from events.registration.utils import get_pricings_for_list
from events.registration.forms import RegistrantForm, RegistrationForm
from events.registration.formsets import RegistrantBaseFormSet
from events.addons.forms import RegAddonForm
from events.addons.formsets import RegAddonBaseFormSet
from events.addons.utils import get_active_addons, get_available_addons

def ajax_user(request, event_id):
    """Ajax query for user validation
    The parameters are email and memberid and pricing.
    The user that matches the given email/memberid will be checked
    if he/she can still register in the event with the given pricing.
    """
    event = get_object_or_404(Event, pk=event_id)
    
    if not get_setting('module', 'events', 'anonymousmemberpricing'):
        raise Http404
    
    memberid = request.GET.get('memberid', None)
    email = request.GET.get('email', None)
    pricingid = request.GET.get('pricingid', None)
    
    pricing = get_object_or_404(RegConfPricing, pk=pricingid)
    
    user = AnonymousUser()
    
    allow_memberid = get_setting('module', 'events', 'memberidpricing')
    if memberid and allow_memberid:# memberid takes priority over email
        memberships = Membership.objects.filter(member_number=memberid)
        if memberships:
            user = memberships[0].user
    elif email:
        users = User.objects.filter(email=email)
        if users:
            user = users[0]
    
    data = json.dumps(None)
    #check if already registered
    if not (user.is_anonymous() or pricing.allow_anonymous):
        used = Registrant.objects.filter(user=user)
        if used:
            if not (pricing.allow_anonymous or is_admin(user)):
                data = json.dumps({"error":"REG"})
            else:
                data = json.dumps({"message":"REG"})
    
    #check if can use
    can_use = can_use_pricing(event, user, pricing)
    if not can_use:
        if not get_setting('module', 'events', 'sharedpricing'):
            data = json.dumps({"error":"INVALID"})
        else:
            data = json.dumps({"error":"SHARED"})
    
    return HttpResponse(data, mimetype="text/plain")
        

@csrf_exempt
def ajax_pricing(request, event_id, template_name="events/registration/pricing.html"):
    """Ajax query for pricing info.
    The parameters are email and memberid.
    Both are not unique to a user but are assumed to be unique.
    On cases that there are multiple matches,
    the first match will be the basis of the pricing list.
    If the setting "sharedpricing" is enabled this ajax check will consider
    the emails associated with the session.
    """
    event = get_object_or_404(Event, pk=event_id)
    
    if not get_setting('module', 'events', 'anonymousmemberpricing'):
        raise Http404
    
    memberid = request.GET.get('memberid', None)
    email = request.GET.get('email', None)
    
    user = AnonymousUser()
    allow_memberid = get_setting('module', 'events', 'memberidpricing')
    shared_pricing = get_setting('module', 'events', 'sharedpricing')
    
    if memberid and allow_memberid:# memberid takes priority over email
        memberships = Membership.objects.filter(member_number=memberid)
        if memberships:
            user = memberships[0].user
    elif email:
        users = User.objects.filter(email=email)
        if users:
            user = users[0]
    
    all_pricings = get_active_pricings(event)
    
    if shared_pricing:
        user_pks = request.session.get('user_list', [])
        if not user.is_anonymous():
            user_pks.append(user.pk)
        request.session['user_list'] = user_pks
        users = User.objects.filter(pk__in=user_pks)
        available_pricings = get_pricings_for_list(event, users)
    else:
        available_pricings = get_available_pricings(event, user)
    
    pricing_list = []
    for pricing in all_pricings:
        p_dict = {
            'title':pricing.title,
            'quantity':pricing.quantity,
            'price':str(pricing.price),
            'pk':pricing.pk,
            'enabled':True,
            'is_public':pricing.allow_anonymous,
        }
        
        if pricing not in available_pricings:
            p_dict['enabled'] = False
        
        pricing_list.append(p_dict)
    
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
    active_pricings = get_active_pricings(event)
    event_pricings = event.registration_configuration.regconfpricing_set.all()
    
    # get available addons
    active_addons = get_active_addons(event)
    
    # start the form set factory    
    RegistrantFormSet = formset_factory(
        RegistrantForm,
        formset=RegistrantBaseFormSet,
        can_delete=True,
        extra=0,
    )
    
    RegAddonFormSet = formset_factory(
        RegAddonForm,
        formset=RegAddonBaseFormSet,
        extra=1,
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
        addon_formset = RegAddonFormSet(request.POST,
                            prefix='addons',
                            event=event,
                            extra_params={
                                'addons':active_addons,
                            })
        
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
        addon_formset = RegAddonFormSet(
                            prefix='addons',
                            event=event,
                            extra_params={
                                'addons':active_addons,
                            })
    
    sets = reg_formset.get_sets()
    
    return render_to_response(template_name, {
            'event':event,
            'reg_form':reg_form,
            'registrant': reg_formset,
            'addon_formset': addon_formset,
            'sets': sets,
            'addons':active_addons,
            'pricings':active_pricings,
            'allow_memberid_pricing':get_setting('module', 'events', 'memberidpricing'),
            'shared_pricing':get_setting('module', 'events', 'sharedpricing'),
            }, context_instance=RequestContext(request))
