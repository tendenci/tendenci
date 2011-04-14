import re
import calendar
from datetime import datetime
from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.template.loader import render_to_string
from django.template.defaultfilters import date as date_filter
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory

from haystack.query import SearchQuerySet

from base.http import Http403
from site_settings.utils import get_setting
from events.models import Event, RegistrationConfiguration, \
    Registration, Registrant, Speaker, Organizer, Type, PaymentMethod, \
    Group, GroupRegistrationConfiguration
from events.forms import EventForm, Reg8nForm, Reg8nEditForm, \
    PlaceForm, SpeakerForm, OrganizerForm, TypeForm, MessageAddForm, \
    RegistrationForm, RegistrantForm, RegistrantBaseFormSet, \
    GroupReg8nEditForm
from events.search_indexes import EventIndex
from events.utils import save_registration, email_registrants, add_registration
from perms.utils import has_perm, get_notice_recipients, update_perms_and_save, get_administrators
from event_logs.models import EventLog
from invoices.models import Invoice
from meta.models import Meta as MetaTags
from meta.forms import MetaForm
from files.models import File


try:
    from notification import models as notification
except:
    notification = None


def index(request, id=None, template_name="events/view.html"):

    if not id:
        return HttpResponseRedirect(reverse('event.month'))

    event = get_object_or_404(Event, pk=id)

    if has_perm(request.user, 'events.view_event', event):

        EventLog.objects.log(
            event_id=175000,  # view event
            event_data='%s (%d) viewed by %s' %
                (event._meta.object_name, event.pk, request.user),
            description='%s viewed' % event._meta.object_name,
            user=request.user,
            request=request,
            instance=event
        )

        speakers = event.speaker_set.all().order_by('pk')
        try:
            organizer = event.organizer_set.all().order_by('pk')[0]
        except:
            organizer = None

        return render_to_response(template_name, {
            'event': event,
            'speakers': speakers,
            'organizer': organizer,
            'now': datetime.now(),
            },
            context_instance=RequestContext(request))
    else:
        raise Http403


def search(request, template_name="events/search.html"):
    query = request.GET.get('q', None)
    events = Event.objects.search(query, user=request.user)

    EventLog.objects.log(
        event_id=174000,  # searched event
        event_data='%s searched by %s' % ('Event', request.user),
        description='Event searched',
        user=request.user,
        request=request,
        source='events',
    )

    return render_to_response(
        template_name,
        {'events': events, 'now': datetime.now()},
        context_instance=RequestContext(request)
    )


def icalendar(request):
    import re
    from events.utils import get_vevents
    p = re.compile(r'http(s)?://(www.)?([^/]+)')
    d = {}

    d['site_url'] = get_setting('site', 'global', 'siteurl')
    match = p.search(d['site_url'])
    if match:
        d['domain_name'] = match.group(3)
    else:
        d['domain_name'] = ""

    ics_str = "BEGIN:VCALENDAR\n"
    ics_str += "PRODID:-//Schipul Technologies//Schipul Codebase 5.0 MIMEDIR//EN\n"
    ics_str += "VERSION:2.0\n"
    ics_str += "METHOD:PUBLISH\n"
    
    # function get_vevents in events.utils
    ics_str += get_vevents(request, d)
    
    ics_str += "END:VCALENDAR\n"
    
    response = HttpResponse(ics_str)
    response['Content-Type'] = 'text/calendar'
    if d['domain_name']:
        file_name = '%s.ics' % (d['domain_name'])
    else:
        file_name = "event.ics"
    response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
    return response
    

def print_view(request, id, template_name="events/print-view.html"):
    event = get_object_or_404(Event, pk=id)    

    EventLog.objects.log(
        event_id =  175001, # print-view event-id
        event_data = '%s (%d) viewed [print] by %s' % (event._meta.object_name, event.pk, request.user),
        description = '%s viewed [print]' % event._meta.object_name,
        user = request.user,
        request = request,
        instance = event
    )

    if has_perm(request.user,'events.view_event',event):
        return render_to_response(template_name, {'event': event}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def handle_uploaded_file(f, instance):
    import os
    from settings import MEDIA_ROOT

    file_name = re.sub(r'[^a-zA-Z0-9._]+', '-', f.name)

    relative_directory = os.path.join(
        'files',
        instance._meta.app_label,
        instance._meta.module_name,
        unicode(instance.pk),
    )

    absolute_directory = os.path.join(MEDIA_ROOT, relative_directory)

    if not os.path.exists(absolute_directory):
        os.makedirs(absolute_directory)

    destination = open(os.path.join(absolute_directory, file_name), 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

    # relative path
    return os.path.join(relative_directory, file_name)

@login_required
def edit(request, id, form_class=EventForm, template_name="events/edit.html"):
    event = get_object_or_404(Event, pk=id)
    SpeakerFormSet = modelformset_factory(Speaker, form=SpeakerForm, extra=2)
    GrpRegFormSet = modelformset_factory(GroupRegistrationConfiguration, form=GroupReg8nEditForm, extra=2)
    # tried get_or_create(); but get a keyword argument :(
    try: # look for an organizer
        organizer = event.organizer_set.all()[0]
    except: # else: create an organizer
        organizer = Organizer()
        organizer.save()
        organizer.event = [event]
        organizer.save()

    if has_perm(request.user,'events.change_event',event):    
        if request.method == "POST":

            form_event = form_class(request.POST, instance=event, user=request.user)
            if form_event.is_valid():
                event = form_event.save(commit=False)
                
                # update all permissions and save the model
                event = update_perms_and_save(request, form_event, event)
                
                EventLog.objects.log(
                    event_id =  172000, # edit event
                    event_data = '%s (%d) edited by %s' % (event._meta.object_name, event.pk, request.user),
                    description = '%s edited' % event._meta.object_name,
                    user = request.user,
                    request = request,
                    instance = event,
                )

                # location validation
                form_place = PlaceForm(request.POST, instance=event.place, 
                    prefix='place')
                if form_place.is_valid():
                    place = form_place.save() # save place
                    event.place = place
                    event.save() # save event

                # speaker validation
                form_speaker = SpeakerFormSet(request.POST, 
                    request.FILES, queryset=event.speaker_set.all(), 
                    prefix = 'speaker')
                if form_speaker.is_valid():
                    speakers = form_speaker.save()
                    for speaker in speakers:
                        speaker.event = [event]
                        speaker.save()
                        File.objects.save_files_for_instance(request, speaker)

                # organizer validation
                form_organizer = OrganizerForm(request.POST, instance=organizer, prefix='organizer')
                if form_organizer.is_valid():
                    organizer = form_organizer.save(commit=False)                   
                    organizer.event = [event]
                    organizer.save()

                # registration configuration validation
                form_regconf = Reg8nEditForm(request.POST, instance=event.registration_configuration, prefix='regconf')
                if form_regconf.is_valid():
                    regconf = form_regconf.save() # save registration configuration
                    event.registration_configuration = regconf
                    event.save() # save event
                    
                form_grpregconf = GrpRegFormSet(request.POST,
                    queryset=event.registration_configuration.groupregistrationconfiguration_set.all(),
                    prefix='grpregconf')
                    
                if form_grpregconf.is_valid():
                    grpregconfs = form_grpregconf.save()
                    for conf in grpregconfs:
                        conf.config = event.registration_configuration
                        conf.save()
                
                forms = [
                    form_event,
                    form_place,
                    form_speaker,
                    form_grpregconf,
                    form_organizer,
                    form_regconf,
                ]

                if all([form.is_valid() for form in forms]):
                    messages.add_message(request, messages.INFO, 'Successfully updated %s' % event)
                    # notification to administrator(s) and module recipient(s)
                    
                    recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
                    if recipients and notification:
                        notification.send_emails(recipients, 'event_added', {
                            'event':event,
                            'user':request.user,
                            'registrants_paid':event.registrants(with_balance=False),
                            'registrants_pending':event.registrants(with_balance=True),
                            'SITE_GLOBAL_SITEDISPLAYNAME': get_setting('site', 'global', 'sitedisplayname'),
                            'SITE_GLOBAL_SITEURL': get_setting('site', 'global', 'siteurl'),
                        })
                    return HttpResponseRedirect(reverse('event', args=[event.pk]))
        else:

            form_event = form_class(instance=event, user=request.user)
            form_place = PlaceForm(instance=event.place, prefix='place')
            form_speaker = SpeakerFormSet(queryset=event.speaker_set.all(), 
                prefix='speaker')
            form_organizer = OrganizerForm(instance=organizer, 
                prefix='organizer')
            form_regconf = Reg8nEditForm(instance=event.registration_configuration, 
                prefix='regconf')
            form_grpregconf = GrpRegFormSet(
                    queryset=event.registration_configuration.groupregistrationconfiguration_set.all(),
                    prefix='grpregconf')

        # response
        return render_to_response(template_name, {
            'event': event,
            'multi_event_forms':[form_event,form_place,form_organizer,form_regconf],
            'form_event':form_event,
            'form_place':form_place,
            'form_speaker':form_speaker,
            'form_organizer':form_organizer,
            'form_regconf':form_regconf,
            'form_grpregconf':form_grpregconf,
            }, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="events/edit-meta.html"):

    # check permission
    event = get_object_or_404(Event, pk=id)
    if not has_perm(request.user,'events.change_event',event):
        raise Http403

    defaults = {
        'title': event.get_title(),
        'description': event.get_description(),
        'keywords': event.get_keywords(),
        'canonical_url': event.get_canonical_url(),
    }
    event.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=event.meta)
        if form.is_valid():
            event.meta = form.save() # save meta
            event.save() # save relationship
            
            messages.add_message(request, messages.INFO, 'Successfully updated meta for %s' % event)
             
            return HttpResponseRedirect(reverse('event', args=[event.pk]))
    else:
        form = form_class(instance=event.meta)

    return render_to_response(template_name, {'event': event, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def add(request, form_class=EventForm, template_name="events/add.html"):
    SpeakerFormSet = modelformset_factory(Speaker, form=SpeakerForm, extra=2)
    GrpRegFormSet = modelformset_factory(GroupRegistrationConfiguration, form=GroupReg8nEditForm, extra=2)
    if has_perm(request.user,'events.add_event'):
        if request.method == "POST":
            
            form_event = form_class(request.POST, user=request.user)
            form_place = PlaceForm(request.POST, prefix='place')
            form_speaker = SpeakerFormSet(request.POST, request.FILES,
                queryset=Speaker.objects.none(), prefix='speaker')
            form_organizer = OrganizerForm(request.POST, 
                prefix='organizer')
            form_regconf = Reg8nEditForm(request.POST, prefix='regconf')
            form_grpregconf = GrpRegFormSet(request.POST,
                queryset=GroupRegistrationConfiguration.objects.none(),
                prefix='grpregconf')
                
            forms = [
                form_event,
                form_place,
                form_speaker,
                form_organizer,
                form_regconf,
                form_grpregconf,
            ]

            if all([form.is_valid() for form in forms]):

                # pks have to exist; before making relationships
                place = form_place.save()
                regconf = form_regconf.save()
                speakers = form_speaker.save()
                organizer = form_organizer.save()
                grpregconfs = form_grpregconf.save()
                event = form_event.save(commit=False)
                
                # update all permissions and save the model
                event = update_perms_and_save(request, form_event, event)
                
                for speaker in speakers:
                    speaker.event = [event]
                    speaker.save()
                    File.objects.save_files_for_instance(request, speaker)
                    
                for grpconf in grpregconfs:
                    grpconf.config = regconf
                    grpconf.save()
                    
                organizer.event = [event]
                organizer.save() # save again

                # update event
                event.place = place
                event.registration_configuration = regconf
                event.save()

                EventLog.objects.log(
                    event_id =  171000, # add event
                    event_data = '%s (%d) added by %s' % (event._meta.object_name, event.pk, request.user),
                    description = '%s added' % event._meta.object_name,
                    user = request.user,
                    request = request,
                    instance = event
                )

                messages.add_message(request, messages.INFO, 'Successfully added %s' % event)
                # notification to administrator(s) and module recipient(s)
                recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
                if recipients and notification:
                    notification.send_emails(recipients, 'event_added', {
                        'event':event,
                        'user':request.user,
                        'registrants_paid':event.registrants(with_balance=False),
                        'registrants_pending':event.registrants(with_balance=True),
                        'SITE_GLOBAL_SITEDISPLAYNAME': get_setting('site', 'global', 'sitedisplayname'),
                        'SITE_GLOBAL_SITEURL': get_setting('site', 'global', 'siteurl'),
                    })

                return HttpResponseRedirect(reverse('event', args=[event.pk]))
        else:
            reg_inits = {
                'early_dt': datetime.now(),
                'regular_dt': datetime.now(),
                'late_dt': datetime.now(),
                'end_dt': datetime.now(),
             }

            form_event = form_class(user=request.user)
            form_place = PlaceForm(prefix='place')
            form_speaker = SpeakerFormSet(queryset=Speaker.objects.none(),
                prefix='speaker')
            form_organizer = OrganizerForm(prefix='organizer')
            form_regconf = Reg8nEditForm(initial=reg_inits, prefix='regconf')
            form_grpregconf = GrpRegFormSet(queryset=GroupRegistrationConfiguration.objects.none(),
                prefix='grpregconf',
                )
            
        # response
        return render_to_response(template_name, {
            'multi_event_forms':[form_event,form_place,form_organizer,form_regconf],
            'form_event':form_event,
            'form_place':form_place,
            'form_speaker':form_speaker,
            'form_organizer':form_organizer,
            'form_regconf':form_regconf,
            'form_grpregconf':form_grpregconf,
            },
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def delete(request, id, template_name="events/delete.html"):
    event = get_object_or_404(Event, pk=id)

    if has_perm(request.user,'events.delete_event'):   
        if request.method == "POST":

            eventlog = EventLog.objects.log(
                event_id =  173000, # delete event
                event_data = '%s (%d) deleted by %s' % (event._meta.object_name, event.pk, request.user),
                description = '%s deleted' % event._meta.object_name,
                user = request.user,
                request = request,
                instance = event
            )

            messages.add_message(request, messages.INFO, 'Successfully deleted %s' % event)
            if notification: notification.send_emails(get_administrators(),'event_deleted', {'object': event, 'request': request})

            # send email to admins
            recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
            if recipients and notification:
                notification.send_emails(recipients,'event_deleted', {
                    'event':event,
                    'user':request.user,
                    'registrants_paid':event.registrants(with_balance=False),
                    'registrants_pending':event.registrants(with_balance=True),
                    'eventlog_url': reverse('event_log', args=[eventlog.pk]),
                    'SITE_GLOBAL_SITEDISPLAYNAME': get_setting('site', 'global', 'sitedisplayname'),
                    'SITE_GLOBAL_SITEURL': get_setting('site', 'global', 'siteurl'),
                })

            event.delete()

            return HttpResponseRedirect(reverse('event.search'))
    
        return render_to_response(template_name, {'event': event}, 
            context_instance=RequestContext(request))
    else:
        raise Http403# Create your views here.

def register(request, event_id=0, form_class=Reg8nForm):
        event = get_object_or_404(Event, pk=event_id)

        # check if event allows registration
        if not event.registration_configuration and \
           event.registration_configuration.enabled:
            raise Http404

        # choose template
        free_reg8n = event.registration_configuration.price <= 0
        if free_reg8n:
            template_name = "events/reg8n/register-free.html"
        else:
            template_name = "events/reg8n/register-priced.html"

        # if logged in; use their info to register
        if request.user.is_authenticated():
            user, email = request.user, request.user.email
        else:
            user, email = None, ''

        # get registrants for this event
        registrants = Registrant.objects.filter(
            registration__event = event,
        )

        # if person is registered; show them their confirmation
        if email:
            if registrants.filter(email=email).exists():
                return HttpResponseRedirect(
                    reverse('event.registration_confirmation',
                    args=(event_id, registrants.filter(email=email)[0].hash)),
                )

        infinite_limit = event.registration_configuration.limit <= 0

        # pull registrants based off "payment required"
        if event.registration_configuration.payment_required:
            registrants = registrants.filter(registration__invoice__balance__lte = 0)

        bad_scenarios = [
            event.end_dt < datetime.now(), # event has passed
            event.registration_configuration.end_dt and event.registration_configuration.end_dt < datetime.now(), # registration period has passed
            event.registration_configuration.early_dt > datetime.now(), # registration period has not started
            (event.registration_configuration.limit <= registrants.count()) and \
                not infinite_limit, # registration limit exceeded
        ]

        if any(bad_scenarios):
            return HttpResponseRedirect(reverse('event', args=(event_id,)))

        if request.method == "POST":
            form = form_class(event_id, request.POST, user=user)
            if form.is_valid():
                price = form.cleaned_data['price']
                payment_method = form.cleaned_data['payment_method']

                reg_defaults = {
                    'user': user,
                    'phone': form.cleaned_data.get('phone', ''),
                    'email': form.cleaned_data.get('email', email),
                    'first_name': form.cleaned_data.get('first_name', ''),
                    'last_name': form.cleaned_data.get('last_name', ''),
                    'company_name': form.cleaned_data.get('company_name', ''),
                    'event': event,
                    'payment_method': payment_method,
                    'price': price,
                }

                # create registration record; then take payment
                # this allows someone to be registered with an outstanding balance
                # gets or creates records
                reg8n, reg8n_created = save_registration(**reg_defaults)

                site_label = get_setting('site', 'global', 'sitedisplayname')
                site_url = get_setting('site', 'global', 'siteurl')
                self_reg8n = get_setting('module', 'users', 'selfregistration')

                is_credit_card_payment = reg8n.payment_method and \
                    (reg8n.payment_method.label).lower() == 'credit card'

                if is_credit_card_payment:
                # online payment

                    # get invoice; redirect to online pay
                    # ------------------------------------

                    invoice = Invoice.objects.get(
                        object_type = ContentType.objects.get(
                        app_label=reg8n._meta.app_label,
                        model=reg8n._meta.module_name),
                        object_id = reg8n.id,
                    )

                    response = HttpResponseRedirect(reverse(
                        'payments.views.pay_online',
                        args=[invoice.id, invoice.guid]
                    ))

                else:
                # offline payment

                    # send email; add message; redirect to confirmation
                    # --------------------------------------------------

                    notification.send_emails(
                        [reg_defaults['email']],
                        'event_registration_confirmation',
                        {   'site_label': site_label,
                            'site_url': site_url,
                            'self_reg8n': self_reg8n,
                            'reg8n': reg8n,
                            'event': event,
                            'price': price,
                            'is_paid': reg8n.invoice.balance == 0
                         },
                        True, # save notice in db
                    )

                    if reg8n.registrant.cancel_dt:
                        messages.add_message(request, messages.INFO,
                            'Your registration was canceled on %s' % date_filter(reg8n.cancel_dt)
                        )
                    elif not reg8n_created:
                        messages.add_message(request, messages.INFO,
                            'You were already registered on %s' % date_filter(reg8n.create_dt)
                        )

                    response = HttpResponseRedirect(reverse(
                        'event.registration_confirmation',
                        args=(event_id, reg8n.registrant.hash)
                    ))

            else: # else form is invalid
                response = render_to_response(template_name, {'event':event, 'form':form}, 
                context_instance=RequestContext(request))

                log_defaults = {
                    'event_id' : 431000,
                    'event_data': '%s (%d) added by %s' % (event._meta.object_name, event.pk, request.user),
                    'description': '%s registered for event %s' % (request.user, event.get_absolute_url()),
                    'user': request.user,
                    'request': request,
                    'instance': event,
                }
                EventLog.objects.log(**log_defaults)

        else: # else request.method != "POST"
            if request.user.is_authenticated():
                payment_method = PaymentMethod.objects.get(pk=3)

                if free_reg8n:
                    reg_defaults = {
                       'user': user,
                       'email': user.email,
                       'first_name': user.first_name,
                       'last_name': user.last_name,
                       'company_name': '',
                       'event': event,
                       'payment_method': payment_method,
                       'price': '0.00',
                    }
                     # if free event; then register w/o payment method
                    reg8n, created = save_registration(**reg_defaults)
                    response = HttpResponseRedirect(reverse(
                        'event.registration_confirmation', 
                        args=(event_id, reg8n.registrant.hash)
                    ))
                else:
                # else prompt registrant w/ registration-form
                    form = form_class(event_id, user=request.user)
                    response = render_to_response(template_name, {'event':event, 'form':form}, 
                        context_instance=RequestContext(request))
            else: # not authenticated
                
                form = form_class(event_id, user=request.user)
                response = render_to_response(template_name, {'event':event, 'form':form}, 
                    context_instance=RequestContext(request))

        return response
    
def multi_register(request, event_id=0, template_name="events/reg8n/multi_register.html"):
    event = get_object_or_404(Event, pk=event_id)

    # check if event allows registration
    if not event.registration_configuration and \
       event.registration_configuration.enabled:
        raise Http404
    
    if not event.registration_configuration.within_time:
            messages.add_message(request, messages.INFO,
                                'Registration has been closed.')
            return HttpResponseRedirect(reverse('event', args=(event_id),))
    
    event_price = event.registration_configuration.price 
    
    RegistrantFormSet = formset_factory(RegistrantForm, formset=RegistrantBaseFormSet,
                                         can_delete=True, max_num=1)
    total_regt_forms = 1
    
    # REGISTRANT formset
    post_data = request.POST or None
     
    if request.method <> 'POST':
        # set the initial data if logged in
        initial = {}
        if request.user.is_authenticated():
            try:
                profile = request.user.get_profile()
            except:
                profile = None
            initial = {'first_name':request.user.first_name,
                        'last_name':request.user.last_name,
                        'email':request.user.email,}
            if profile:
                initial.update({'company_name': profile.company,
                                'phone':profile.phone,})
        registrant = RegistrantFormSet(prefix='registrant',
                                       initial=[initial], event=event)
    else: 
        if post_data and 'add_registrant' in request.POST:
            post_data = request.POST.copy()
            post_data['registrant-TOTAL_FORMS'] = int(post_data['registrant-TOTAL_FORMS'])+ 1  
        registrant = RegistrantFormSet(post_data, prefix='registrant', event=event)
    
    # REGISTRATION form
    if request.method == 'POST' and 'submit' in request.POST:
        reg_form = RegistrationForm(event, request.POST, user=request.user)
    else:
        reg_form = RegistrationForm(event, user=request.user)
    if request.user.is_authenticated():
        del reg_form.fields['captcha']
    
    # total registrant forms    
    if post_data:
        total_regt_forms = post_data['registrant-TOTAL_FORMS']
    
    if request.method == 'POST':
        if 'submit' in request.POST:
            if reg_form.is_valid() and registrant.is_valid():
                reg8n, reg8n_created = add_registration(request, event, reg_form, registrant)
                
                site_label = get_setting('site', 'global', 'sitedisplayname')
                site_url = get_setting('site', 'global', 'siteurl')
                self_reg8n = get_setting('module', 'users', 'selfregistration')
                
                is_credit_card_payment = reg8n.payment_method and \
                (reg8n.payment_method.label).lower() == 'credit card'
                
                
                if reg8n_created:
                    if is_credit_card_payment:
                        # online payment
                        # get invoice; redirect to online pay
                        
                        return HttpResponseRedirect(reverse(
                                                'payments.views.pay_online',
                                                args=[reg8n.invoice.id, reg8n.invoice.guid]
                                                )) 
                    else:
                        # offline payment:
                        # send email; add message; redirect to confirmation
                        print reg8n.registrant.hash
                        notification.send_emails(
                            [reg8n.registrant.email],
                            'event_registration_confirmation',
                            {   'site_label': site_label,
                                'site_url': site_url,
                                'self_reg8n': self_reg8n,
                                'reg8n': reg8n,
                                'event': event,
                                'price': event_price,
                                'is_paid': reg8n.invoice.balance == 0
                             },
                            True, # save notice in db
                        )
                        
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
                
                else:
                    messages.add_message(request, messages.INFO,
                                 'You were already registered on %s' % date_filter(reg8n.create_dt)
                    ) 
                           
                return HttpResponseRedirect(reverse( 
                                                'event.registration_confirmation',
                                                args=(event_id, reg8n.registrant.hash)
                                                ))         

    
    total_price = 0
    free_event = event_price <= 0
        
    # if not free event, store price in the list for each registrant
    #if not free_event:
    price_list = []
    i = 0
    for form in registrant.forms:
        deleted = False
        if form.data.get('registrant-%d-DELETE' % i, False):
            deleted = True
        price_list.append({'price':event_price, 'deleted':deleted})
        if not deleted:
            total_price += event_price
        i = i+1
        
    # check if we have any error on registrant formset
    has_registrant_form_errors = False
    for form in registrant.forms:
        for field in form:
            if field.errors:
                has_registrant_form_errors = True
                break
        if has_registrant_form_errors:
            break

    return render_to_response(template_name, {'event':event, 
                                              'reg_form':reg_form,
                                               'registrant': registrant,
                                               'total_regt_forms': total_regt_forms,
                                               'free_event': free_event,
                                               'price_list':price_list,
                                               'total_price':total_price,
                                               'has_registrant_form_errors': has_registrant_form_errors,
                                               }, 
                    context_instance=RequestContext(request))
    
def registration_edit(request, reg8n_id=0, hash='', template_name="events/reg8n/reg8n_edit.html"):
    reg8n = get_object_or_404(Registration, pk=reg8n_id)
    
    # check permission
    boo = False
    if has_perm(request.user, 'events.change_registration', reg8n) or \
        (hash and reg8n.registrant.hash == hash):
        boo = True
            
    if not boo:
        raise Http403
    
    RegistrantFormSet = modelformset_factory(Registrant, extra=0,
                                fields=('first_name', 'last_name', 'email', 'phone', 'company_name'))
    formset = RegistrantFormSet(request.POST or None,
                                queryset=Registrant.objects.filter(registration=reg8n).order_by('id'))
    
    # required fields only stay on the first form
    for i, form in enumerate(formset.forms):
        for key in form.fields.keys():
            if i > 0:
                form.fields[key].required = False
            else:
                if key in ['phone', 'company_name']:
                    form.fields[key].required = False
        
    
    if request.method == 'POST':
        if formset.is_valid():
            instances = formset.save()
            
            reg8n_conf_url = reverse( 
                                    'event.registration_confirmation',
                                    args=(reg8n.event.id, reg8n.registrant.hash)
                                    )
        
            if instances:
            
                # log an event
                log_defaults = {
                    'event_id' : 202000,
                    'event_data': '%s (%d) edited by %s' % (reg8n._meta.object_name, reg8n.pk, request.user),
                    'description': '%s edited registrants info for event registrations %s' % (request.user, reg8n_conf_url),
                    'user': request.user,
                    'request': request,
                    'instance': reg8n,
                }
                EventLog.objects.log(**log_defaults)
                
                msg = 'Registrant(s) info updated'
            else:
                msg = 'No changes made to the registrant(s)'
            
            messages.add_message(request, messages.INFO, msg) 
                    
            return HttpResponseRedirect(reg8n_conf_url)  
   
   
    total_regt_forms = Registrant.objects.filter(registration=reg8n).count()
    
    # check formset error
    formset_errors = False
    for form in formset.forms:
        for field in form:
            if field.errors:
                formset_errors = True
                break
        if formset_errors:
            break
    
    
    return render_to_response(template_name, {'formset': formset,
                                              'formset_errors':formset_errors,
                                              'total_regt_forms':total_regt_forms,
                                              'reg8n': reg8n,
                                               }, 
                    context_instance=RequestContext(request))


def cancel_registration(request, event_id=0, registrant_id=0, hash='', template_name="events/reg8n/cancel.html"):
    event = get_object_or_404(Event, pk=event_id)
    if registrant_id:
        try:
            registrant = Registrant.objects.get(
                registration__event = event,
                pk = registrant_id,
            )

            # check permission
            if not has_perm(request.user, 'events.view_registrant', registrant):
                raise Http403
        except:
            raise Http404

    elif hash:
        sqs = SearchQuerySet()
        sqs = sqs.models(Registrant)
        sqs = sqs.filter(event_pk=event.pk)
        sqs = sqs.auto_query(sqs.query.clean(hash))
        sqs = sqs.order_by("-update_dt")

        try:
            registrant = sqs[0].object
        except:
            raise Http404
        
    user_is_registrant = False
    if not request.user.is_anonymous() and registrant.user:
        if request.user.id == registrant.user.id:
            user_is_registrant = True

    if request.method == "POST":
        # check if already canceled. if so, do nothing
        if not registrant.cancel_dt:
            registrant.cancel_dt = datetime.now()
            registrant.save()
            
            # update the amount_paid in registration
            if registrant.amount:
                if registrant.registration.amount_paid:
                    registrant.registration.amount_paid -= registrant.amount
                    registrant.registration.save()
                
                # update the invoice if invoice is not tendered
                invoice = registrant.registration.invoice
                if not invoice.is_tendered:
                    invoice.total -= registrant.amount
                    invoice.subtotal -= registrant.amount
                    invoice.balance -= registrant.amount
                    invoice.save(request.user)
            

            recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
            if recipients and notification:
                notification.send_emails(recipients, 'event_registration_cancelled', {
                    'event':event,
                    'user':request.user,
                    'registrants_paid':event.registrants(with_balance=False),
                    'registrants_pending':event.registrants(with_balance=True),
                    'SITE_GLOBAL_SITEDISPLAYNAME': get_setting('site', 'global', 'sitedisplayname'),
                    'SITE_GLOBAL_SITEURL': get_setting('site', 'global', 'siteurl'),
                    'registrant':registrant,
                    'user_is_registrant': user_is_registrant,
                })

        # back to invoice
        return HttpResponseRedirect(
            reverse('event.registration_confirmation', args=[event.pk, registrant.hash]))
        
    return render_to_response(template_name, {
        'event': event,
        'registrant':registrant,
        'hash': hash,
        'user_is_registrant': user_is_registrant,
        }, 
        context_instance=RequestContext(request))

def month_view(request, year=None, month=None, type=None, template_name='events/month-view.html'):
    from datetime import date
    from events.utils import next_month, prev_month

    if type: # redirect to /events/month/ if type does not exist
        if not Type.objects.search('slug:%s' % type):
            return HttpResponseRedirect(reverse('event.month'))

    # default/convert month and year
    if month and year:
        month, year = int(month), int(year)
    else:
        month, year = datetime.now().month, datetime.now().year

    calendar.setfirstweekday(calendar.SUNDAY)
    Calendar = calendar.Calendar

    next_month, next_year = next_month(month, year)
    prev_month, prev_year = prev_month(month, year)

    # remove any params that aren't set (e.g. type)
    next_month_params = [i for i in (next_year, next_month, type) if i]
    prev_month_params = [i for i in (prev_year, prev_month, type) if i]

    next_month_url = reverse('event.month', args=next_month_params)
    prev_month_url = reverse('event.month', args=prev_month_params)

    month_names = calendar.month_name[month-1:month+2]
    weekdays = calendar.weekheader(10).split()
    cal = Calendar(calendar.SUNDAY).monthdatescalendar(year, month)

    types = Type.objects.all().order_by('name')

    return render_to_response(template_name, {
        'cal':cal, 
        'month':month,
        'prev_month_url':prev_month_url,
        'next_month_url':next_month_url,
        'month_names':month_names,
        'year':year,
        'weekdays':weekdays,
        'types':types,
        'type':type,
        'date': date,
        }, 
        context_instance=RequestContext(request))

def day_view(request, year=None, month=None, day=None, template_name='events/day-view.html'):

    kwargs = {
        # i'm being explicit about each date part
        # because I do not want to include the time
        'start_dt__day': day,
        'start_dt__month': month,
        'start_dt__year': year,
    }

    events = Event.objects.filter(**kwargs).order_by('start_dt')
    
    return render_to_response(template_name, {
        'events': events,
        'date': datetime(year=int(year), month=int(month), day=int(day)),
        'now':datetime.now()
        }, 
        context_instance=RequestContext(request))

@login_required
def types(request, template_name='events/types/index.html'):
    from django.forms.models import modelformset_factory
    TypeFormSet = modelformset_factory(Type, form=TypeForm, extra=2, can_delete=True)

    if request.method == 'POST':
        formset = TypeFormSet(request.POST)
        if formset.is_valid():
            formset.save()

            # log "added" event_types
            for event_type in formset.new_objects:
                EventLog.objects.log(**{
                    'event_id' : 271000,
                    'event_data': '%s (%d) added by %s' % (event_type._meta.object_name, event_type.pk, request.user),
                    'description': '%s added' % event_type._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': event_type,
                })

            # log "changed" event_types
            for event_type, changed_data in formset.changed_objects:
                EventLog.objects.log(**{
                    'event_id' : 272000,
                    'event_data': '%s (%d) edited by %s' % (event_type._meta.object_name, event_type.pk, request.user),
                    'description': '%s edited' % event_type._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': event_type,
                })

            # log "deleted" event_types
            for event_type in formset.deleted_objects:
                EventLog.objects.log(**{
                    'event_id' : 273000,
                    'event_data': '%s deleted by %s' % (event_type._meta.object_name, request.user),
                    'description': '%s deleted' % event_type._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': event_type,
                })

    formset = TypeFormSet()

    return render_to_response(template_name, {'formset': formset}, 
        context_instance=RequestContext(request))

@login_required
def registrant_search(request, event_id=0, template_name='events/registrants/search.html'):
    query = request.GET.get('q', None)

    event = get_object_or_404(Event, pk=event_id)
    registrants = Registrant.objects.search(
        query, user=request.user, event=event,).order_by("-update_dt")

    return render_to_response(template_name, {'event':event, 'registrants':registrants}, 
        context_instance=RequestContext(request))

# http://127.0.0.1/events/4/registrants/roster/total
@login_required
def registrant_roster(request, event_id=0, roster_view='', template_name='events/registrants/roster.html'):
    # roster_view in ['total', 'paid', 'non-paid']
    from django.db.models import Sum
    event = get_object_or_404(Event, pk=event_id)
    query = ''

    if not roster_view: # default to total page
        return HttpResponseRedirect(reverse('event.registrant.roster.total', args=[event.pk]))

    # is:paid or is:non-paid
#    if 'paid' in roster_view:
#        query = '"is:%s"' % roster_view
#
#    query = '%s "is:confirmed"' % query
#    registrants = Registrant.objects.search(
#            query, user=request.user, event=event).order_by('last_name')
    # paid or non-paid or total
    registrations = Registration.objects.filter(event=event)
    if roster_view == 'paid':
        registrations = registrations.filter(invoice__balance=0)
    elif roster_view == 'non-paid':
        registrations = registrations.filter(invoice__balance__gt=0)

    # grab the primary registrants then the additional registrants 
    # to group the registrants with the same registration together
    primary_registrants = []
    for registration in registrations:
        regs = registration.registrant_set.filter(cancel_dt = None).order_by("pk")
        if regs:
            primary_registrants.append(regs[0])
    primary_registrants = sorted(primary_registrants, key=lambda reg: reg.last_name)
    
    registrants = []
    for primary_reg in primary_registrants:
        registrants.append(primary_reg)
        for reg in primary_reg.additional_registrants:
            registrants.append(reg)

    total_sum = float(0)
    balance_sum = float(0)

    # get total and balance (sum)
    for reg8n in registrations:
        if not reg8n.canceled:  # not cancelled
            if roster_view != 'paid':
                total_sum += float(reg8n.invoice.total)
            balance_sum += float(reg8n.invoice.balance)

    num_registrants_who_payed = event.registrants(with_balance=False).count()
    num_registrants_who_owe = event.registrants(with_balance=True).count()

    return render_to_response(template_name, {
        'event':event, 
        'registrants':registrants,
        'balance_sum':balance_sum,
        'total_sum':total_sum,
        'num_registrants_who_payed':num_registrants_who_payed,
        'num_registrants_who_owe':num_registrants_who_owe,
        'roster_view':roster_view,
        },
        context_instance=RequestContext(request))

@login_required
def registrant_details(request, id=0, hash='', template_name='events/registrants/details.html'):
    registrant = get_object_or_404(Registrant, pk=id)

    if has_perm(request.user,'registrants.view_registrant',registrant):
        return render_to_response(template_name, {'registrant': registrant}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def registration_confirmation(request, id=0, reg8n_id=0, hash='', 
    template_name='events/reg8n/register-confirm.html'):
    """ Registration confirmation """

    event = get_object_or_404(Event, pk=id)
    count_registrants = 1
    
    if reg8n_id:

        # URL is obvious
        # permission check

        try:
            registration = Registration.objects.get(
                event = event,
                pk = reg8n_id,
            )
    
            # check permission
            if not has_perm(request.user, 'events.view_registration', registration):
                raise Http403
            
            # for now, just get a list of registrants
            registrants = registration.registrant_set.all().order_by('id')
            count_registrants = registration.registrant_set.count()
            registrant = registrants[0]

        except:
            raise Http404

    elif hash:
        sqs = SearchQuerySet()
        sqs = sqs.models(Registrant)
        sqs = sqs.filter(event_pk=event.pk)
        sqs = sqs.auto_query(sqs.query.clean(hash))
        sqs = sqs.order_by("-update_dt")

        try:
            registrant = sqs[0].object
            registration = registrant.registration
            
            registrants = registration.registrant_set.all().order_by('id')
            count_registrants = registration.registrant_set.count()
        except:
            raise Http404

    return render_to_response(template_name, {
        'event':event,
        'registrant':registrant,
        'registration':registration,
        'registrants': registrants,
        'count_registrants': count_registrants,
        'hash': hash,
        }, 
        context_instance=RequestContext(request))
    
@login_required
def message_add(request, event_id, form_class=MessageAddForm, template_name='events/message/add.html'):
    from emails.models import Email
    event = get_object_or_404(Event, pk=event_id)
    if not has_perm(request.user,'events.change_event',event): raise Http403

    if request.method == "POST":
        email = Email()
        form = form_class(event.id, request.POST, instance=email)

        if form.is_valid():

            email.sender = get_setting('site', 'global', 'siteemailnoreplyaddress')
            email.sender = email.sender or request.user.email

            email.sender_display = request.user.get_full_name()
            email.reply_to = request.user.email
            email.recipient = request.user.email
            email.content_type = "text/html"
            email.subject = '%s notice from %s' % (event.title, get_setting('site', 'global', 'sitedisplayname'))
            email.save(request.user)
            subject = email.subject

            registrant_kwargs = {}
            registrant_kwargs['payment_status'] = form.cleaned_data['payment_status']
            email_registrants(event, email, **registrant_kwargs)

            registrant_kwargs['summary'] = '<font face=""Arial"" color=""#000000"">'
            registrant_kwargs['summary'] += 'Emails sent as a result of Calendar Event Notification</font><br><br>'
            registrant_kwargs['summary'] += '<font face=""Arial"" color=""#000000"">'
            registrant_kwargs['summary'] += '<br><br>Email Sent Appears Below in Raw Format'
            registrant_kwargs['summary'] += '</font><br><br>'
            registrant_kwargs['summary'] += email.body

            # send summary
            email.subject = 'SUMMARY: %s' % email.subject
            email.body = registrant_kwargs['summary']
            email.recipient = request.user.email
            email.send()
            
            # send another copy to the site webmaster
            email.recipient = get_setting('site', 'global', 'sitewebmasteremail')
            if email.recipient:
                email.subject = 'WEBMASTER SUMMARY: %s' % email.subject
                email.body = '<h2>Site Webmaster Notification of Calendar Event Send</h2>%s' % email.body
                email.send()

            EventLog.objects.log(**{
                'event_id' : 131101,
                'event_data': '%s (%d) sent by %s to event registrants' % (email._meta.object_name, email.pk, request.user),
                'description': '%s (%d) sent to event registrants of %s' % (email._meta.object_name, email.pk, event.title),
                'user': request.user,
                'request': request,
                'instance': email,
            })
            
            messages.add_message(request, messages.INFO, 'Successfully sent email "%s" to event registrants for event "%s".' % (subject, event.title))
            
            return HttpResponseRedirect(reverse('event', args=([event_id])))
        
    else:
        openingtext = render_to_string('events/message/opening-text.txt', {'event': event}, 
            context_instance=RequestContext(request))
        form = form_class(event.id, initial={'body': openingtext})
    
    return render_to_response(template_name, {
        'event':event,
        'form': form
        },context_instance=RequestContext(request))


def registrant_export(request, event_id, roster_view=''):
    """
    Export all registration for a specific event
    """
    event = get_object_or_404(Event, pk=event_id)

    # if they can edit it, they can export it
    if not has_perm(request.user,'events.change_event',event):
        raise Http403

    import xlwt
    from ordereddict import OrderedDict
    from decimal import Decimal

    # create the excel book and sheet
    book = xlwt.Workbook(encoding='utf8')
    sheet = book.add_sheet('Registrants')

    if roster_view == 'non-paid':
        registrants = event.registrants(with_balance=True)
        file_name = event.title.strip().replace(' ','-')
        file_name = 'Event-%s-Non-Paid.xls' % re.sub(r'[^a-zA-Z0-9._]+', '', file_name)
    elif roster_view == 'paid':
        registrants = event.registrants(with_balance=False)
        file_name = event.title.strip().replace(' ','-')
        file_name = 'Event-%s-Paid.xls' % re.sub(r'[^a-zA-Z0-9._]+', '', file_name)
    else:
        registrants = event.registrants()
        file_name = event.title.strip().replace(' ','-')
        file_name = 'Event-%s-Total.xls' % re.sub(r'[^a-zA-Z0-9._]+', '', file_name)

    # the key is what the column will be in the
    # excel sheet. the value is the database lookup
    # Used OrderedDict to maintain the column order
    registrant_mappings = OrderedDict([
        ('first_name', 'first_name'),
        ('last_name', 'last_name'),
        ('phone', 'phone'),
        ('email', 'email'),
        ('registration_id', 'registration__pk'),
        ('invoice_id', 'registration__invoice__pk'),
        ('registration price', 'registration__amount_paid'),
        ('payment method', 'registration__payment_method__label'),
        ('balance', 'registration__invoice__balance'),
        ('company', 'company_name'),
        ('address', 'address'),
        ('city', 'city'),
        ('state', 'state'),
        ('zip', 'zip'),
        ('country', 'country'),
        ('date', 'create_dt'),
    ])
    registrant_lookups = registrant_mappings.values()

    # Append the heading to the list of values that will
    # go into the excel sheet
    values_list = []
    values_list.insert(0, registrant_mappings.keys())

    # excel date styles
    balance_owed_style = xlwt.easyxf('font: color-index red, bold on')
    default_style = xlwt.Style.default_style
    datetime_style = xlwt.easyxf(num_format_str='mm/dd/yyyy hh:mm')
    date_style = xlwt.easyxf(num_format_str='mm/dd/yyyy')

#    if registrations:
#        # bulk of the work happens here
#        # loop through all the registrations and append the output
#        # of values_list django method to the values_list list
#        for registration in registrations:
#            registrants = registration.registrant_set.all()
#            registrants = registrants.exclude(cancel_dt__isnull=False)
#            registrants = registrants.values_list(*registrant_lookups)
#            for registrant in registrants:
#                values_list.append(registrant)

    for registrant in registrants.values_list(*registrant_lookups):
        values_list.append(registrant)

    # Write the data enumerated to the excel sheet
    for row, row_data in enumerate(values_list):
        for col, val in enumerate(row_data):
            # styles the date/time fields
            if isinstance(val, datetime):
                style = datetime_style
            elif isinstance(val, date):
                style = date_style
            else:
                style = default_style
                
            # style the invoice balance column
            if col == 7:
                balance = val
                if not val:
                    balance = 0
                if val is None:
                    balance = 0
                if isinstance(balance,Decimal) and balance > 0:
                    style = balance_owed_style

            sheet.write(row, col, val, style=style)

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s' % file_name
    book.save(response)
    return response



