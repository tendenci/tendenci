import re
import calendar
from datetime import datetime
from datetime import date, timedelta
from decimal import Decimal

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.http import QueryDict
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
    RegConfPricing
from events.forms import EventForm, Reg8nForm, Reg8nEditForm, \
    PlaceForm, SpeakerForm, OrganizerForm, TypeForm, MessageAddForm, \
    RegistrationForm, RegistrantForm, RegistrantBaseFormSet, \
    Reg8nConfPricingForm
from events.search_indexes import EventIndex
from events.utils import save_registration, email_registrants, add_registration
from events.utils import registration_has_started, get_pricing, clean_price
from events.utils import get_event_spots_taken, update_event_spots_taken
from events.utils import get_ievent, copy_event, email_admins, get_active_days
from perms.utils import has_perm, get_notice_recipients, \
    update_perms_and_save, get_administrators, is_admin
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
    
    if not event.on_weekend:
        days = get_active_days(event)
    else:
        days = []
    
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
            'days':days,
            },
            context_instance=RequestContext(request))
    else:
        raise Http403


def search(request, template_name="events/search.html"):
    query = request.GET.get('q', None)
    if query:
        events = Event.objects.search(query, user=request.user)
    else:
        # load upcoming events only by default
        events = Event.objects.search(date_range=(datetime.now(), None), user=request.user)

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

def icalendar_single(request, id):
    import re
    from events.utils import get_vevents
    p = re.compile(r'http(s)?://(www.)?([^/]+)')
    d = {}

    if not Event.objects.filter(pk=id).exists():
        raise Http404

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
    ics_str += get_ievent(request, d, id)
    
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
    SpeakerFormSet = modelformset_factory(
        Speaker, 
        form=SpeakerForm,
        extra=1,
        can_delete=True
    )
    RegConfPricingSet = modelformset_factory(
        RegConfPricing, 
        form=Reg8nConfPricingForm,
        extra=0,
        can_delete=True
    )

    # tried get_or_create(); but get a keyword argument :(
    try: # look for an organizer
        organizer = event.organizer_set.all()[0]
    except: # else: create an organizer
        organizer = Organizer()
        organizer.save()
        organizer.event = [event]
        organizer.save()

    if has_perm(request.user,'events.change_event', event):    
        if request.method == "POST":
            # single forms
            form_event = form_class(request.POST, instance=event, user=request.user)
            form_place = PlaceForm(request.POST, instance=event.place, prefix='place')
            form_organizer = OrganizerForm(
                request.POST,
                instance=organizer, 
                prefix='organizer'
            )
            form_regconf = Reg8nEditForm(
                request.POST,
                instance=event.registration_configuration, 
                prefix='regconf'
            )

            # form sets
            form_speaker = SpeakerFormSet(
                request.POST, 
                request.FILES,
                queryset=event.speaker_set.all(),
                prefix='speaker'
            )

            form_regconfpricing = RegConfPricingSet(
                request.POST,
                queryset=RegConfPricing.objects.filter(
                    reg_conf=event.registration_configuration,
                    status=True,
                ),
                prefix='regconfpricing'
            )
                
            # label the form sets
            form_speaker.label = "Speaker(s)"
            form_regconfpricing.label = "Pricing(s)"

            forms = [
                form_event,
                form_place,
                form_speaker,
                form_organizer,
                form_regconf,
                form_regconfpricing
            ]

            if all([form.is_valid() for form in forms]):
                # pks have to exist; before making relationships
                place = form_place.save()
                regconf = form_regconf.save()
                speakers = form_speaker.save()
                organizer = form_organizer.save()
                regconf_pricing = form_regconfpricing.save()

                event = form_event.save(commit=False)

                # update all permissions and save the model
                event = update_perms_and_save(request, form_event, event)

                # make dict (i.e. speaker_bind); bind speaker with speaker image
                pattern = re.compile('speaker-\d+-name')
                speaker_keys = list(set(re.findall(pattern, ' '.join(request.POST))))
                speaker_bind = {}
                for speaker_key in speaker_keys:  # loop through speaker form items
                    speaker_name = request.POST.get(speaker_key)
                    if speaker_name:  # if speaker name found in request
                        speaker_file = request.FILES.get(speaker_key.replace('name','file'))
                        if speaker_file:  # if speaker file found in request
                            # e.g. speaker_bind['eloy zuniga'] = <file>
                            speaker_bind[speaker_name] = speaker_file

                for speaker in speakers:
                    speaker.event = [event]
                    speaker.save()

                    # match speaker w/ speaker image
                    binary_files = []
                    if speaker.name in speaker_bind:
                        binary_files = [speaker_bind[speaker.name]]
                    files = File.objects.save_files_for_instance(request, speaker, files=binary_files)

                    for f in files:
                        f.allow_anonymous_view = event.allow_anonymous_view
                        f.allow_user_view = event.allow_user_view
                        f.allow_member_view = event.allow_member_view
                        f.save()

                for regconf_price in regconf_pricing:
                    regconf_price.reg_conf = regconf
                    regconf_price.save()
                    
                organizer.event = [event]
                organizer.save() # save again

                # update event
                event.place = place
                event.registration_configuration = regconf
                event.save()

                EventLog.objects.log(
                    event_id =  172000, # edit event
                    event_data = '%s (%d) edited by %s' % (event._meta.object_name, event.pk, request.user),
                    description = '%s edited' % event._meta.object_name,
                    user = request.user,
                    request = request,
                    instance = event,
                )

                messages.add_message(request, messages.INFO, 'Successfully updated %s' % event)
                return HttpResponseRedirect(reverse('event', args=[event.pk]))
        else:
            # single forms
            form_event = form_class(instance=event, user=request.user)
            form_place = PlaceForm(instance=event.place, prefix='place')

            form_organizer = OrganizerForm(
                instance=organizer, 
                prefix='organizer'
            )
            form_regconf = Reg8nEditForm(
                instance=event.registration_configuration, 
                prefix='regconf'
            )

            # form sets
            form_speaker = SpeakerFormSet(
                queryset=event.speaker_set.all(),
                prefix='speaker',
                auto_id='speaker_formset'
            )

            form_regconfpricing = RegConfPricingSet(
                queryset=RegConfPricing.objects.filter(
                    reg_conf=event.registration_configuration,
                    status=True,
                ),
                prefix='regconfpricing',
                auto_id='regconfpricing_formset'
            )

            # label the form sets
            form_speaker.label = "Speaker(s)"
            form_regconfpricing.label = "Pricing(s)"

        # response
        return render_to_response(template_name, {
            'event': event,
            'multi_event_forms':[
                form_event,
                form_place,
                form_organizer,
                form_speaker,
                form_regconf,
                form_regconfpricing
                ],
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
def add(request, year=None, month=None, day=None, \
    form_class=EventForm, template_name="events/add.html"):
    """
    Add event page.  You can preset the start date of
    the event by traveling to the appropriate URL.
    """
    SpeakerFormSet = modelformset_factory(
        Speaker, 
        form=SpeakerForm, 
        extra=1
    )
    RegConfPricingSet = modelformset_factory(
        RegConfPricing, 
        form=Reg8nConfPricingForm, 
        extra=1
    )


    if has_perm(request.user,'events.add_event'):
        if request.method == "POST":
            
            # single forms
            form_event = form_class(request.POST, user=request.user)
            form_place = PlaceForm(request.POST, prefix='place')
            form_organizer = OrganizerForm(request.POST, prefix='organizer')
            form_regconf = Reg8nEditForm(request.POST, prefix='regconf')

            # form sets
            form_speaker = SpeakerFormSet(
                request.POST, 
                request.FILES,
                queryset=Speaker.objects.none(), 
                prefix='speaker'
            )

            form_regconfpricing = RegConfPricingSet(
                request.POST,
                queryset=RegConfPricing.objects.none(),
                prefix='regconfpricing'
            )
                
            # label the form sets
            form_speaker.label = "Speaker(s)"
            form_regconfpricing.label = "Pricing(s)"

            forms = [
                form_event,
                form_place,
                form_speaker,
                form_organizer,
                form_regconf,
                form_regconfpricing
            ]

            if all([form.is_valid() for form in forms]):

                # pks have to exist; before making relationships
                place = form_place.save()
                regconf = form_regconf.save()
                speakers = form_speaker.save()
                organizer = form_organizer.save()
                regconf_pricing = form_regconfpricing.save()

                event = form_event.save(commit=False)

                # update all permissions and save the model
                event = update_perms_and_save(request, form_event, event)
                
                for speaker in speakers:
                    speaker.event = [event]
                    speaker.save()
                    files = File.objects.save_files_for_instance(request, speaker)
                    # set file permissions
                    for f in files:
                        f.allow_anonymous_view = event.allow_anonymous_view
                        f.allow_user_view = event.allow_user_view
                        f.allow_member_view = event.allow_member_view
                        f.save()
                    
                for regconf_price in regconf_pricing:
                    regconf_price.reg_conf = regconf
                    regconf_price.save()
                    
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
        else:  # if not post request
            event_init = {}

            today = datetime.today()
            offset = timedelta(hours=2)
            
            if all((year, month, day)):
                date_str = '-'.join([year,month,day])
                time_str = '10:00 AM'
                dt_str = "%s %s" % (date_str, time_str)
                dt_fmt = '%Y-%m-%d %H:%M %p'
                
                start_dt = datetime.strptime(dt_str, dt_fmt)
                end_dt = datetime.strptime(dt_str, dt_fmt) + offset
                
                event_init['start_dt'] = start_dt
                event_init['end_dt'] = end_dt
            else:
                start_dt = datetime.now()
                end_dt = datetime.now() + offset
                
                event_init['start_dt'] = start_dt
                event_init['end_dt'] = end_dt
            
            reg_init = {
                'start_dt':start_dt,
                'end_dt':end_dt,
            }
            
            # single forms
            form_event = form_class(user=request.user, initial=event_init)
            form_place = PlaceForm(prefix='place')
            form_organizer = OrganizerForm(prefix='organizer')
            form_regconf = Reg8nEditForm(initial=reg_init, prefix='regconf')
            
            # form sets
            form_speaker = SpeakerFormSet(
                queryset=Speaker.objects.none(),
                prefix='speaker',
                auto_id='speaker_formset'
            )

            form_regconfpricing = RegConfPricingSet(
                queryset=RegConfPricing.objects.none(),
                prefix='regconfpricing',
                auto_id='regconfpricing_formset'
            )

            # label the form sets
            form_speaker.label = "Speaker(s)"
            form_regconfpricing.label = "Pricing(s)"

        # response
        return render_to_response(template_name, {
            'multi_event_forms':[
                form_event,
                form_place,
                form_organizer,
                form_speaker,
                form_regconf,
                form_regconfpricing
                ],
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

            # send email to admins
            recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
            if recipients and notification:
                notification.send_emails(recipients,'event_deleted', {
                    'event':event,
                    'request':request,
                    'user':request.user,
                    'registrants_paid':event.registrants(with_balance=False),
                    'registrants_pending':event.registrants(with_balance=True),
                    'eventlog_url': reverse('event_log', args=[eventlog.pk]),
                    'SITE_GLOBAL_SITEDISPLAYNAME': get_setting('site', 'global', 'sitedisplayname'),
                    'SITE_GLOBAL_SITEURL': get_setting('site', 'global', 'siteurl'),
                })

            # The one-to-one relationship is on events which 
            # doesn't delete the registration_configuration record.
            # The delete must occur on registration_configuration
            # for both to be deleted. An honest accident on 
            # one-to-one fields. 
            try:
                event.registration_configuration.delete()
            except:
                event.delete()

            return HttpResponseRedirect(reverse('event.search'))
    
        return render_to_response(template_name, {'event': event}, 
            context_instance=RequestContext(request))
    else:
        raise Http403# Create your views here.


def multi_register_redirect(request, event, msg):
    messages.add_message(request, messages.INFO, msg)
    return HttpResponseRedirect(reverse('event', args=(event.pk,),))    


def multi_register(request, event_id=0, template_name="events/reg8n/multi_register.html"):
    """
    This view has 2 POST states. Instead of a GET and a POST.
    Attempting to access this view via GET will redirect to the event 
    page. The 2 POST states both require 'pricing' in request.POST.
    The first POST state comes from the event page where the price 
    selections take place.
    It is identified by the presence of 'from_price_form' in request.POST.
    The second POST state comes from the page rendered by this form.
    It is identified by the presense of 'submit' in request.POST and 
    absence of 'from_price_form'.
    """
    event = get_object_or_404(Event, pk=event_id)

    # check if event allows registration
    if not event.registration_configuration and \
       event.registration_configuration.enabled:
        raise Http404

    # set up pricing
    try:
        price, price_pk, amount = clean_price(request.POST['price'], request.user)
    except:
        return multi_register_redirect(request, event, _('Please choose a price.'))
        
    # set the event price that will be used throughout the view
    event_price = amount
    
    # get all pricing
    pricing = RegConfPricing.objects.filter(
        reg_conf=event.registration_configuration,
        status=True,
    )
    
    # check is this person is qualified to see this pricing and event_price
    qualified_pricing = get_pricing(request.user, event, pricing=pricing)
    qualifies = False
    for q_price in qualified_pricing:
        if price.pk == q_price['price'].pk:
            qualifies = True
    if not qualifies:
        return multi_register_redirect(request, event, _('Please choose a price.'))

    # check if this post came from the pricing form
    # and modify the request method
    # we want it to fake a get here so that
    # the client can't actually see the pricing
    # var
    if 'from_price_form' in request.POST:
        request.method = 'GET'
        request.POST = QueryDict({})

    # check if it is still open based on dates
    reg_started = registration_has_started(event, pricing=pricing)
    if not reg_started:
        return multi_register_redirect(request, event, _('Registration has been closed.'))     

    # update the spots left
    limit = event.registration_configuration.limit
    spots_taken = 0
    if limit > 0:
        spots_taken = get_event_spots_taken(event)
        if spots_taken > limit:
            return multi_register_redirect(request, event, _('Registration is full.'))

    # start the form set factory    
    RegistrantFormSet = formset_factory(
        RegistrantForm, 
        formset=RegistrantBaseFormSet,
        can_delete=True,
        max_num=price.quantity,
        extra=(price.quantity - 1)
    )

    # update the amount of forms based on quantity
    total_regt_forms = price.quantity

    # REGISTRANT formset
    post_data = request.POST or None
     
    if request.method != 'POST':
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
        reg_form = RegistrationForm(
            event,
            price,
            event_price,
            request.POST, 
            user=request.user,
            count=len(registrant.forms),
        )
    else:
        reg_form = RegistrationForm(
            event,
            price,
            event_price,
            user=request.user
        )
    if request.user.is_authenticated():
        del reg_form.fields['captcha']
    
    # total registrant forms    
    if post_data:
        total_regt_forms = post_data['registrant-TOTAL_FORMS']
    
    if request.method == 'POST':
        if 'submit' in request.POST:
            if reg_form.is_valid() and registrant.is_valid():
                
                # override event_price to price specified by admin
                admin_notes = ''
                if is_admin(request.user) and event_price > 0:
                    if event_price != reg_form.cleaned_data['amount_for_admin']:
                        admin_notes = "Price has been overriden for this registration. "
                    event_price = reg_form.cleaned_data['amount_for_admin']
                
                # apply discount if any
                discount = reg_form.get_discount()
                if discount:
                    event_price = event_price - discount.value
                    if event_price < 0:
                        event_price = 0
                    admin_notes = "%sDiscount code: %s has been enabled for this registration." % (admin_notes, discount.discount_code)
                    #messages.add_message(request, messages.INFO,
                    #    'Your discount of $%s has been added.' % discount.value
                    #)
                    
                reg8n, reg8n_created = add_registration(
                    request, 
                    event, 
                    reg_form, 
                    registrant,
                    price,
                    event_price,
                    admin_notes = admin_notes,
                    discount = discount,
                )
                
                site_label = get_setting('site', 'global', 'sitedisplayname')
                site_url = get_setting('site', 'global', 'siteurl')
                self_reg8n = get_setting('module', 'users', 'selfregistration')
                
                is_credit_card_payment = reg8n.payment_method and \
                (reg8n.payment_method.machine_name).lower() == 'credit-card' \
                and event_price > 0
                
                if reg8n_created:
                    # update the spots taken on this event
                    update_event_spots_taken(event)

                    if is_credit_card_payment:
                        # online payment
                        # get invoice; redirect to online pay
                        # email the admins as well
                        email_admins(event, event_price, self_reg8n, reg8n)
                        
                        return HttpResponseRedirect(reverse(
                            'payments.views.pay_online',
                            args=[reg8n.invoice.id, reg8n.invoice.guid]
                        )) 
                    else:
                        # offline payment:
                        # send email; add message; redirect to confirmation
                        if reg8n.registrant.email:
                            notification.send_emails(
                                [reg8n.registrant.email],
                                'event_registration_confirmation',
                                {   
                                    'site_label': site_label,
                                    'site_url': site_url,
                                    'self_reg8n': self_reg8n,
                                    'reg8n': reg8n,
                                    'event': event,
                                    'price': event_price,
                                    'is_paid': reg8n.invoice.balance == 0
                                 },
                                True, # save notice in db
                            )                            
                            #email the admins as well
                            email_admins(event, event_price, self_reg8n, reg8n)
                        
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
    
    # if not free event, store price in the list for each registrant
    price_list = []
    count = 0
    total_price = Decimal(str(0.00))
    free_event = event_price <= 0

    for form in registrant.forms:
        deleted = False
        if form.data.get('registrant-%d-DELETE' % count, False):
            deleted = True
        if count % price.quantity == 0:
            price_list.append({'price': event_price, 'deleted':deleted})
        else:
            price_list.append({'price': 0.00 , 'deleted':deleted})
        if not deleted:
            if price.quantity > 1:
                total_price = event_price
            else:
                total_price += event_price
        count += 1
        
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
                                              'event_price': event_price,
                                              'free_event': free_event,
                                              'price_list':price_list,
                                              'total_price':total_price,
                                              'price': price,
                                              'reg_form':reg_form,
                                              'registrant': registrant,
                                              'total_regt_forms': total_regt_forms,
                                              'has_registrant_form_errors': has_registrant_form_errors,
                                               }, 
                    context_instance=RequestContext(request))
    
def registration_edit(request, reg8n_id=0, hash='', template_name="events/reg8n/reg8n_edit.html"):
    reg8n = get_object_or_404(Registration, pk=reg8n_id)

    perms = (
        has_perm(request.user, 'events.change_registration', reg8n),  # has perm
        reg8n.registrant.hash == hash  # has secret hash
    )

    if not any(perms):
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


def cancel_registration(request, event_id, registration_id, hash='', template_name="events/reg8n/cancel_registration.html"):
    event = get_object_or_404(Event, pk=event_id)

    try:
        registration = Registration.objects.get(
            event=event,
            pk=registration_id,
        )
    except Registration.DoesNotExist as e:
        raise Http404

    if hash:
        if hash != registration.hash:
            raise Http404
    else:  # check permission
        if not has_perm(request.user, 'events.view_registration', registration):
            raise Http403     

    registrants = registration.registrant_set.filter(cancel_dt__isnull=True)
    cancelled_registrants = registration.registrant_set.filter(cancel_dt__isnull=False)

    if request.method == "POST":
        # check if already canceled. if so, do nothing
        if not registration.canceled:
            for registrant in registrants:
                user_is_registrant = False
                if not request.user.is_anonymous() and registrant.user:
                    if request.user.id == registrant.user.id:
                        user_is_registrant = True

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
            
            # update the spots taken on this event
            update_event_spots_taken(event)

        return HttpResponseRedirect(
            reverse('event.registration_confirmation', 
            args=[event.pk, registrant.hash])
        )
        
    return render_to_response(template_name, {
        'event': event,
        'registration': registration,
        'registrants': registrants,
        'cancelled_registrants': cancelled_registrants,
        'hash': hash,
        }, 
        context_instance=RequestContext(request))


def cancel_registrant(request, event_id=0, registrant_id=0, hash='', template_name="events/reg8n/cancel_registrant.html"):
    event = get_object_or_404(Event, pk=event_id)

    if registrant_id:
        try:
            registrant = Registrant.objects.get(
                registration__event=event,
                pk =registrant_id,
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

    if registrant.cancel_dt:
        raise Http404

    if request.method == "POST":
        # check if already canceled. if so, do nothing
        if not registrant.cancel_dt:
            user_is_registrant = False
            if not request.user.is_anonymous() and registrant.user:
                if request.user.id == registrant.user.id:
                    user_is_registrant = True

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

            # update the spots taken on this event
            update_event_spots_taken(event)

        # back to invoice
        return HttpResponseRedirect(
            reverse('event.registration_confirmation', args=[event.pk, registrant.hash]))
        
    return render_to_response(template_name, {
        'event': event,
        'registrant':registrant,
        'hash': hash,
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
    
    if year < 1900:
        raise Http404

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
    year = int(year)
    if year < 1900:
        raise Http404
    
    return render_to_response(template_name, {
        'date': datetime(year=int(year), month=int(month), day=int(day)),
        'now':datetime.now(),
        'type':None,
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
                    'source': 'events',
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
                    'source': 'events',
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
                    'source': 'events',
                })

    formset = TypeFormSet()

    return render_to_response(template_name, {'formset': formset}, 
        context_instance=RequestContext(request))

@login_required
def registrant_search(request, event_id=0, template_name='events/registrants/search.html'):
    query = request.GET.get('q', None)

    event = get_object_or_404(Event, pk=event_id)
    registrants = Registrant.objects.search(
        query, user=request.user, event=event).order_by("-update_dt")

    active_registrants = Registrant.objects.search(
        "is:active", user=request.user, event=event).order_by("-update_dt")

    canceled_registrants = Registrant.objects.search(
        "is:canceled", user=request.user, event=event).order_by("-update_dt")

    return render_to_response(template_name, {
        'event':event, 
        'registrants':registrants,
        'active_registrants':active_registrants,
        'canceled_registrants':canceled_registrants,
        }, context_instance=RequestContext(request))

# http://127.0.0.1/events/4/registrants/roster/total
@login_required
def registrant_roster(request, event_id=0, roster_view='', template_name='events/registrants/roster.html'):
    # roster_view in ['total', 'paid', 'non-paid']
    from django.db.models import Sum
    event = get_object_or_404(Event, pk=event_id)
    query = ''

    if not roster_view: # default to total page
        return HttpResponseRedirect(reverse('event.registrant.roster.total', args=[event.pk]))

    # paid or non-paid or total
    registrations = Registration.objects.filter(event=event)
    if roster_view == 'paid':
        registrations = registrations.filter(invoice__balance__lte=0)
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
            if reg8n.invoice != None:
                if roster_view != 'paid':
                    total_sum += float(reg8n.invoice.total)
                balance_sum += float(reg8n.invoice.balance)

    num_registrants_who_paid = event.registrants(with_balance=False).count()
    num_registrants_who_owe = event.registrants(with_balance=True).count()

    return render_to_response(template_name, {
        'event':event, 
        'registrants':registrants,
        'balance_sum':balance_sum,
        'total_sum':total_sum,
        'num_registrants_who_paid':num_registrants_who_paid,
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
    registrants_count = 1
    registrant_hash = hash

    if reg8n_id:
        registration = get_object_or_404(Registration, event=event, pk=reg8n_id)
        if not has_perm(request.user, 'events.view_registration', registration):
            raise Http403

        registrant = registration.registrant

    elif registrant_hash:
        sqs = SearchQuerySet()
        sqs = sqs.models(Registrant)
        sqs = sqs.filter(event_pk=event.pk)
        sqs = sqs.auto_query(sqs.query.clean(registrant_hash))
        sqs = sqs.order_by("-update_dt")

        try:
            registrant = sqs[0].object
            registration = registrant.registration
        except:
            raise Http404

    registrants = registration.registrant_set.all().order_by('id')
    registrants_count = registration.registrant_set.count()

    return render_to_response(template_name, {
        'event':event,
        'registrant':registrant,
        'registration':registration,
        'registrants': registrants,
        'registrants_count': registrants_count,
        'hash': registrant_hash,
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
        ('price type', 'registration__reg_conf_price__title'),
        ('invoice_id', 'registration__invoice__pk'),
        ('registration price', 'registration__amount_paid'),
        ('payment method', 'registration__payment_method__machine_name'),
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

@login_required
def delete_speaker(request, id):
    """
        This delete is designed based on the add and edit view where
        a speaker is considered to only be a speaker for a single event.
    """
    
    if not has_perm(request.user,'events.delete_speaker'):
        raise Http403
        
    speaker = get_object_or_404(Speaker, id = id)
    event = speaker.event.all()[0]
    
    messages.add_message(request, messages.INFO, 'Successfully deleted %s' % speaker)
    
    speaker.delete()
    
    return redirect('event', id=event.id)
    
@login_required
def delete_group_pricing(request, id):
    if not has_perm(request.user,'events.delete_registrationconfiguration'): 
        raise Http403
        
    gp = get_object_or_404(GroupRegistrationConfiguration, id = id)
    event = Event.objects.get(registration_configuration=gp.config)
    
    messages.add_message(request, messages.INFO, 'Successfully deleted Group Pricing for %s' % gp)
    
    gp.delete()
    
    return redirect('event', id=event.id)
    
@login_required
def delete_special_pricing(request, id):
    if not has_perm(request.user,'events.delete_registrationconfiguration'): 
        raise Http403
        
    s = get_object_or_404(SpecialPricing, id = id)
    event = Event.objects.get(registration_configuration=s.config)
    
    messages.add_message(request, messages.INFO, 'Successfully deleted Special Pricing for %s' % s)
    
    s.delete()
    
    return redirect('event', id=event.id)

@login_required
def copy(request, id):
    if not has_perm(request.user, 'events.add_event'):
        raise Http403
        
    event = get_object_or_404(Event, id=id)
    new_event = copy_event(event, request.user)
    
    EventLog.objects.log(
        event_id =  171000, # add event
        event_data = '%s (%d) added by %s' % (new_event._meta.object_name, new_event.pk, request.user),
        description = '%s added' % new_event._meta.object_name,
        user = request.user,
        request = request,
        instance = new_event
    )
    
    messages.add_message(request, messages.INFO, 'Sucessfully copied Event: %s.<br />Edit the new event (set to <strong>private</strong>) below.' % new_event.title)
    
    return redirect('event.edit', id=new_event.id)
