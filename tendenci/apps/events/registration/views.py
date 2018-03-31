"""ANONYMOUS EVENT REGISTRATION VIEWS"""

from builtins import str

from django.contrib import messages
from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext_lazy as _
import simplejson as json
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.forms.formsets import formset_factory
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.forms.models import model_to_dict

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.memberships.models import Membership
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp

from tendenci.apps.events.models import Event, RegConfPricing, Registrant
from tendenci.apps.events.utils import email_admins
from tendenci.apps.events.registration.constants import REG_CLOSED, REG_FULL
from tendenci.apps.events.registration.utils import get_available_pricings, reg_status
from tendenci.apps.events.registration.utils import can_use_pricing, get_active_pricings
from tendenci.apps.events.registration.utils import process_registration, send_registrant_email
from tendenci.apps.events.registration.utils import get_pricings_for_list
from tendenci.apps.events.registration.forms import RegistrantForm, RegistrationForm
from tendenci.apps.events.registration.formsets import RegistrantBaseFormSet
from tendenci.apps.events.addons.forms import RegAddonForm
from tendenci.apps.events.addons.formsets import RegAddonBaseFormSet
from tendenci.apps.events.addons.utils import get_active_addons, get_available_addons, get_addons_for_list
from tendenci.apps.events.forms import FormForCustomRegForm

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
        membership = Membership.objects.first(member_number=memberid)
        if hasattr(membership, 'user'):
            user = membership.user
    elif email:
        users = User.objects.filter(email=email)
        if users:
            user = users[0]

    data = json.dumps(None)
    #check if already registered
    if not (user.is_anonymous or pricing.allow_anonymous):
        used = Registrant.objects.filter(user=user)
        if used:
            if not (pricing.allow_anonymous or user.profile.is_superuser):
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

    return HttpResponse(data, content_type="text/plain")


@csrf_exempt
def ajax_pricing(request, event_id, template_name="events/registration/pricing.html"):
    """Ajax query for pricing info.
    The parameters are email and memberid.
    Both are not unique to a user but are assumed to be unique.
    On cases that there are multiple matches,
    the first match will be the basis of the pricing list.
    If the setting "sharedpricing" is enabled this ajax check will consider
    the emails associated with the session.
    ** This now also returns ADDON info in the same format.
    """
    event = get_object_or_404(Event, pk=event_id)

    if not get_setting('module', 'events', 'anonymousmemberpricing'):
        raise Http404

    memberid = request.GET.get('memberid', None)
    email = request.GET.get('email', None)

    user = AnonymousUser()
    allow_memberid = get_setting('module', 'events', 'memberidpricing')
    shared_pricing = get_setting('module', 'events', 'sharedpricing')

    if memberid and allow_memberid:  # memberid takes priority over email
        membership = Membership.objects.first(member_number=memberid)
        if hasattr(membership, 'user'):
            user = membership.user
    elif email:
        users = User.objects.filter(email=email)
        if users:
            user = users[0]

    # register user in user list
    user_pks = request.session.get('user_list', [])
    if not user.is_anonymous:
        user_pks.append(user.pk)
    request.session['user_list'] = user_pks

    # Set up available pricings
    all_pricings = get_active_pricings(event)
    if shared_pricing:
        # use entire user list
        shareable_users = User.objects.filter(pk__in=user_pks)
        available_pricings = get_pricings_for_list(event, shareable_users)
    else:
        shareable_users = None
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

    all_addons = get_active_addons(event)
    if shared_pricing:
        available_addons = get_addons_for_list(event, shareable_users)
    else:
        available_addons = get_available_addons(event, user)

    a_list = []
    for addon in all_addons:
        d = model_to_dict(addon)
        d['options'] = addon.options
        if addon in available_addons:
            # temporarily allow anon viewing for this email
            d['allow_anonymous'] = True
        a_list.append(d)

    form = render_to_string(template_name='events/addons/addon-add-box.html',
        context={'addons':a_list, 'anon_pricing':True},
        request=request)

    data = json.dumps({
        'pricings':pricing_list,
        'add-addons-form':form,
    })
    return HttpResponse(data, content_type="text/plain")

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
        return redirect('event.multi_register', event_id)

    # clear user list session
    request.session['user_list'] = []

    event = get_object_or_404(Event, pk=event_id)

    # check if event allows registration
    if (event.registration_configuration is None or not event.registration_configuration.enabled):
        raise Http404

    # check if it is still open, always open for admin users
    if not request.user.profile.is_superuser:
        status = reg_status(event, request.user)
        if status == REG_FULL:
            messages.add_message(request, messages.ERROR, _('Registration is full.'))
            return redirect('event', event.pk)
        elif status == REG_CLOSED:
            messages.add_message(request, messages.ERROR, _('Registration is closed.'))
            return redirect('event', event.pk)

    # get available pricings
    active_pricings = get_active_pricings(event)
    event_pricings = event.registration_configuration.regconfpricing_set.all()

    # get available addons
    active_addons = get_active_addons(event)

    # check if use a custom reg form
    custom_reg_form = None
    reg_conf = event.registration_configuration
    if reg_conf.use_custom_reg_form:
        if reg_conf.bind_reg_form_to_conf_only:
            custom_reg_form = reg_conf.reg_form

    #custom_reg_form = None

    if custom_reg_form:
        RF = FormForCustomRegForm
    else:
        RF = RegistrantForm

    # start the form set factory
    RegistrantFormSet = formset_factory(
        RF,
        formset=RegistrantBaseFormSet,
        can_delete=True,
        extra=0,
    )

    RegAddonFormSet = formset_factory(
        RegAddonForm,
        formset=RegAddonBaseFormSet,
        extra=0,
    )

    if request.method == "POST":
        # process the submitted forms
        params = {'prefix': 'registrant',
                 'event': event,
                 'extra_params': {
                                  'pricings':event_pricings,
                                  }
                  }
        if custom_reg_form:
            params['extra_params'].update({"custom_reg_form": custom_reg_form,
                                           'event': event})
        reg_formset = RegistrantFormSet(request.POST,
                            **params)

        reg_form = RegistrationForm(event, request.user, request.POST,
                    reg_count = len(reg_formset.forms))

        # This form is just here to preserve the data in case of invalid registrants
        # The real validation of addons is after validation of registrants
        addon_formset = RegAddonFormSet(request.POST,
                            prefix='addon',
                            event=event,
                            extra_params={
                                'addons':active_addons,
                                'valid_addons':active_addons,
                            })
        addon_formset.is_valid()

        # validate the form and formset
        if False not in (reg_form.is_valid(), reg_formset.is_valid()):
            valid_addons = get_addons_for_list(event, reg_formset.get_user_list())
            # validate the addons
            addon_formset = RegAddonFormSet(request.POST,
                            prefix='addon',
                            event=event,
                            extra_params={
                                'addons':active_addons,
                                'valid_addons':valid_addons,
                            })
            if addon_formset.is_valid():
                # process the registration
                # this will create the registrants and apply the discount
                reg8n = process_registration(reg_form, reg_formset,  addon_formset, custom_reg_form=custom_reg_form)

                self_reg8n = get_setting('module', 'users', 'selfregistration')
                is_credit_card_payment = (reg8n.payment_method and
                    (reg8n.payment_method.machine_name).lower() == 'credit-card'
                    and reg8n.amount_paid > 0)
                registrants = reg8n.registrant_set.all().order_by('id')
                for registrant in registrants:
                    #registrant.assign_mapped_fields()
                    if registrant.custom_reg_form_entry:
                        registrant.name = str(registrant.custom_reg_form_entry)
                    else:
                        registrant.name = ' '.join([registrant.first_name, registrant.last_name])

                if is_credit_card_payment: # online payment
                    # email the admins as well
                    email_admins(event, reg8n.amount_paid, self_reg8n, reg8n, registrants)
                    # get invoice; redirect to online pay
                    return redirect('payment.pay_online',
                        reg8n.invoice.id, reg8n.invoice.guid)
                else:
                    # offline payment
                    # email the registrant
                    send_registrant_email(reg8n, self_reg8n)
                    # email the admins as well
                    email_admins(event, reg8n.amount_paid, self_reg8n, reg8n, registrants)

                EventLog.objects.log(instance=event)

                # redirect to confirmation
                return redirect('event.registration_confirmation', event_id, reg8n.registrant.hash)
    else:
        params = {'prefix': 'registrant',
                    'event': event,
                    'extra_params': {
                        'pricings':event_pricings,
                    }
                  }
        if custom_reg_form:
            params['extra_params'].update({"custom_reg_form": custom_reg_form,
                                           'event': event})
        # intialize empty forms
        reg_formset = RegistrantFormSet(**params)
        reg_form = RegistrationForm(event, request.user)
        addon_formset = RegAddonFormSet(
                            prefix='addon',
                            event=event,
                            extra_params={
                                'addons':active_addons,
                            })

    sets = reg_formset.get_sets()

    # build our hidden form dynamically
    hidden_form = None
    if custom_reg_form:
        params = {'prefix': 'registrant',
                  'event': event,
                  'extra_params': {
                        'pricings':event_pricings,
                        'custom_reg_form': custom_reg_form,
                        'event': event
                    }
                  }
        FormSet = formset_factory(
            FormForCustomRegForm,
            formset=RegistrantBaseFormSet,
            can_delete=True,
            extra=1,
        )
        formset = FormSet(**params)
        hidden_form = formset.forms[0]

    return render_to_resp(request=request, template_name=template_name, context={
            'event':event,
            'reg_form':reg_form,
            'custom_reg_form': custom_reg_form,
            'hidden_form': hidden_form,
            'registrant': reg_formset,
            'addon_formset': addon_formset,
            'sets': sets,
            'addons':active_addons,
            'pricings':active_pricings,
            'anon_pricing':True,
            'total_price':reg_formset.get_total_price()+addon_formset.get_total_price(),
            'allow_memberid_pricing':get_setting('module', 'events', 'memberidpricing'),
            'shared_pricing':get_setting('module', 'events', 'sharedpricing'),
            })
