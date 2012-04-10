import re
import calendar
from datetime import datetime
from datetime import date, timedelta
from decimal import Decimal

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.http import QueryDict
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.template.loader import render_to_string
from django.template.defaultfilters import date as date_filter
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory, inlineformset_factory
from django.forms.models import BaseModelFormSet

from haystack.query import SearchQuerySet
from base.http import Http403
from site_settings.utils import get_setting
from perms.utils import (has_perm, get_notice_recipients, is_admin,
    get_query_filters, update_perms_and_save, get_administrators, has_view_perm)
from event_logs.models import EventLog
from invoices.models import Invoice
from meta.models import Meta as MetaTags
from meta.forms import MetaForm
from files.models import File
from theme.shortcuts import themed_response as render_to_response

from events.search_indexes import EventIndex
from events.models import (Event, RegistrationConfiguration,
    Registration, Registrant, Speaker, Organizer, Type, PaymentMethod,
    RegConfPricing, Addon, AddonOption, RegAddon, CustomRegForm,
    CustomRegFormEntry, CustomRegField, CustomRegFieldEntry)
from events.forms import (EventForm, Reg8nForm, Reg8nEditForm,
    PlaceForm, SpeakerForm, OrganizerForm, TypeForm, MessageAddForm,
    RegistrationForm, RegistrantForm, RegistrantBaseFormSet,
    Reg8nConfPricingForm, PendingEventForm, AddonForm, AddonOptionForm,
    FormForCustomRegForm, RegConfPricingBaseModelFormSet)
from events.utils import (save_registration, email_registrants, 
    add_registration, registration_has_started, get_pricing, clean_price,
    get_event_spots_taken, update_event_spots_taken, get_ievent,
    copy_event, email_admins, get_active_days, get_ACRF_queryset,
    get_custom_registrants_initials, render_registrant_excel)
from events.addons.forms import RegAddonForm
from events.addons.formsets import RegAddonBaseFormSet
from events.addons.utils import (get_active_addons, get_available_addons, 
    get_addons_for_list)

from notification import models as notification
    
def custom_reg_form_preview(request, id, template_name="events/custom_reg_form_preview.html"):
    """
    Preview a custom registration form.
    """    
    form = get_object_or_404(CustomRegForm, id=id)
    
    form_for_form = FormForCustomRegForm(request.POST or None, request.FILES or None, custom_reg_form=form, user=request.user)

    for field in form_for_form.fields:
        try:
            form_for_form.fields[field].initial = request.GET.get(field, '')
        except:
            pass
        
    context = {"form": form, "form_for_form": form_for_form}
    return render_to_response(template_name, context, RequestContext(request))

@login_required
def event_custom_reg_form_list(request, event_id, 
                               template_name="events/event_custom_reg_form_list.html"):
    """
    List custom registration forms for this event.
    """
    event = get_object_or_404(Event, pk=event_id)
    if not has_perm(request.user,'events.change_event', event):
        raise Http403
    
    reg_conf = event.registration_configuration
    regconfpricings = reg_conf.regconfpricing_set.all()
    
    if reg_conf.use_custom_reg_form:
        if reg_conf.bind_reg_form_to_conf_only:
            reg_conf.reg_form.form_for_form = FormForCustomRegForm(custom_reg_form=reg_conf.reg_form)
        else:
            for price in regconfpricings:
                price.reg_form.form_for_form = FormForCustomRegForm(custom_reg_form=price.reg_form)
            
        
    context = {'event': event,
               'reg_conf': reg_conf,
               'regconfpricings': regconfpricings}
    return render_to_response(template_name, context, RequestContext(request))

def details(request, id=None, template_name="events/view.html"):

    if not id:
        return HttpResponseRedirect(reverse('event.month'))

    event = get_object_or_404(Event, pk=id)
    
    days = []
    if not event.on_weekend:
        days = get_active_days(event)

    if not has_view_perm(request.user, 'events.view_event', event):
        raise Http403

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
    organizers = event.organizer_set.all().order_by('pk') or None

    organizer = None
    if organizers:
        organizer = organizers[0]

    return render_to_response(template_name, {
        'days':days,
        'event': event,
        'speakers': speakers,
        'organizer': organizer,
        'now': datetime.now(),
        'addons': event.addon_set.filter(status=True),
    }, context_instance=RequestContext(request))


def month_redirect(request):
    return HttpResponseRedirect(reverse('event.month'))


def search(request, redirect=False, template_name="events/search.html"):
    """
    This page lists out all the upcoming events starting
    from today.  If a search index is available, this page
    also provides the option to search through events.
    """
    if redirect:
        return HttpResponseRedirect(reverse('events'))

    has_index = get_setting('site', 'global', 'searchindex')
    query = request.GET.get('q', None)
    event_type = request.GET.get('event_type', None)
    start_dt = request.GET.get('start_dt', None)
    if isinstance(start_dt, unicode):
        start_dt = datetime.strptime(
            start_dt,
            '%Y-%m-%d'
        )
    else:
        start_dt = datetime.now()

    if has_index and query:
        event_type_obj = Type.objects.filter(slug=event_type)
        if event_type_obj:
            query = "%s type:%s" % (query, event_type_obj[0].name)
        events = Event.objects.search(query, user=request.user)
        events = events.filter(start_dt__gte=start_dt)
    else:
        filters = get_query_filters(request.user, 'events.view_event')
        events = Event.objects.filter(filters).distinct()
        events = events.filter(start_dt__gte=start_dt)
        if event_type:
            events = events.filter(type__slug=event_type)
        if request.user.is_authenticated():
            events = events.select_related()

    events = events.order_by('start_dt')
    types = Type.objects.all().order_by('name')

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
        {'events': events,'types': types, 'now': datetime.now(), 'event_type': event_type, 'start_dt': start_dt},
        context_instance=RequestContext(request)
    )

def icalendar(request):
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

    if has_view_perm(request.user,'events.view_event',event):
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
    # custom reg_form queryset
    reg_form_queryset = get_ACRF_queryset(event)
    regconfpricing_params = {'reg_form_queryset': reg_form_queryset}
    
    SpeakerFormSet = modelformset_factory(
        Speaker, 
        form=SpeakerForm,
        extra=1,
        can_delete=True
    )
    
    if event.registration_configuration.regconfpricing_set.all():
        extra = 0
    else:
        extra = 1

    RegConfPricingSet = modelformset_factory(
        RegConfPricing,
        formset=RegConfPricingBaseModelFormSet,
        form=Reg8nConfPricingForm,
        extra=extra,
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
            form_event = form_class(request.POST, request.FILES, instance=event, user=request.user)
            form_place = PlaceForm(request.POST, instance=event.place, prefix='place')
            form_organizer = OrganizerForm(
                request.POST,
                instance=organizer, 
                prefix='organizer'
            )
            
            form_regconf = Reg8nEditForm(
                request.POST,
                instance=event.registration_configuration, 
                reg_form_queryset=reg_form_queryset,
                prefix='regconf'
            )

            # form sets
            form_speaker = SpeakerFormSet(
                request.POST, 
                request.FILES,
                queryset=event.speaker_set.all(),
                prefix='speaker'
            )
            
            conf_reg_form_required = False      # if reg_form is required on regconf
            pricing_reg_form_required = False  # if reg_form is required on regconfpricing
            if form_regconf.is_valid():
                (use_custom_reg_form, 
                 reg_form_id, 
                 bind_reg_form_to_conf_only
                 ) = form_regconf.cleaned_data['use_custom_reg'].split(',')
                if use_custom_reg_form == '1':
                    if bind_reg_form_to_conf_only == '1':
                        conf_reg_form_required = True
                    else:
                        pricing_reg_form_required = True
                    regconfpricing_params.update({'reg_form_required': pricing_reg_form_required})
                    
            form_regconfpricing = RegConfPricingSet(
                request.POST,
                queryset=RegConfPricing.objects.filter(
                    reg_conf=event.registration_configuration,
                    status=True,
                ),
                prefix='regconfpricing',
                **regconfpricing_params
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
                
                # save photo
                photo = form_event.cleaned_data['photo_upload']
                if photo:
                    event.save(photo=photo)

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

                if not conf_reg_form_required and regconf.reg_form:
                    regconf.reg_form = None
                    regconf.save()
                    
                for regconf_price in regconf_pricing:
                    regconf_price.reg_conf = regconf
                    
                    if not pricing_reg_form_required:
                        regconf_price.reg_form = None
                    
                    regconf_price.save()
                    
                organizer.event = [event]
                organizer.save() # save again

                # update event
                event.place = place
                event.registration_configuration = regconf
                event.save()
                
                # un-tie the reg_form from the pricing
                if not pricing_reg_form_required:
                    for price in regconf.regconfpricing_set.all():
                        if price.reg_form:
                            price.reg_form = None
                            price.save()

                EventLog.objects.log(
                    event_id =  172000, # edit event
                    event_data = '%s (%d) edited by %s' % (event._meta.object_name, event.pk, request.user),
                    description = '%s edited' % event._meta.object_name,
                    user = request.user,
                    request = request,
                    instance = event,
                )

                messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % event)
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
                reg_form_queryset=reg_form_queryset, 
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
                auto_id='regconfpricing_formset',
                **regconfpricing_params
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
            
            messages.add_message(request, messages.SUCCESS, 'Successfully updated meta for %s' % event)
             
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
    # custom reg_form queryset
    reg_form_queryset = get_ACRF_queryset()
    regconfpricing_params = {'reg_form_queryset': reg_form_queryset}
    
    SpeakerFormSet = modelformset_factory(
        Speaker, 
        form=SpeakerForm, 
        extra=1
    )
    RegConfPricingSet = modelformset_factory(
        RegConfPricing, 
        formset=RegConfPricingBaseModelFormSet,
        form=Reg8nConfPricingForm, 
        extra=1
    )
    
    if has_perm(request.user,'events.add_event'):
        if request.method == "POST":
            
            # single forms
            form_event = form_class(request.POST, request.FILES, user=request.user)
            form_place = PlaceForm(request.POST, prefix='place')
            form_organizer = OrganizerForm(request.POST, prefix='organizer')
            form_regconf = Reg8nEditForm(request.POST, prefix='regconf', 
                                         reg_form_queryset=reg_form_queryset,)

            # form sets
            form_speaker = SpeakerFormSet(
                request.POST,
                request.FILES,
                queryset=Speaker.objects.none(),
                prefix='speaker'
            )
            
            conf_reg_form_required = False      # if reg_form is required on regconf
            pricing_reg_form_required = False  # if reg_form is required on regconfpricing
            if form_regconf.is_valid():
                (use_custom_reg_form, 
                 reg_form_id, 
                 bind_reg_form_to_conf_only
                 ) = form_regconf.cleaned_data['use_custom_reg'].split(',')
                if use_custom_reg_form == '1':
                    if bind_reg_form_to_conf_only == '1':
                        conf_reg_form_required = True
                    else:
                        pricing_reg_form_required = True
                    regconfpricing_params.update({'reg_form_required': pricing_reg_form_required})

            form_regconfpricing = RegConfPricingSet(
                request.POST,
                queryset=RegConfPricing.objects.none(),
                prefix='regconfpricing',
                **regconfpricing_params
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
                
                # save photo
                photo = form_event.cleaned_data['photo_upload']
                if photo:
                    event.save(photo=photo)
                
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
                        
                if not conf_reg_form_required and regconf.reg_form:
                    regconf.reg_form = None
                    regconf.save()
                    
                for regconf_price in regconf_pricing:
                    regconf_price.reg_conf = regconf
                    
                    if not pricing_reg_form_required:
                        regconf_price.reg_form = None
                    
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

                messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % event)
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
            form_regconf = Reg8nEditForm(initial=reg_init, prefix='regconf', 
                                         reg_form_queryset=reg_form_queryset,)
            
            # form sets
            form_speaker = SpeakerFormSet(
                queryset=Speaker.objects.none(),
                prefix='speaker',
                auto_id='speaker_formset'
            )

            form_regconfpricing = RegConfPricingSet(
                queryset=RegConfPricing.objects.none(),
                prefix='regconfpricing',
                auto_id='regconfpricing_formset',
                **regconfpricing_params
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

            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % event)

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
        pricing, pricing_pk, amount = clean_price(request.POST['price'], request.user)
    except:
        return multi_register_redirect(request, event, _('Please choose a price.'))
    
    # set the event price that will be used throughout the view
    event_price = amount
    
    # get all pricing
    pricings = RegConfPricing.objects.filter(
        reg_conf=event.registration_configuration,
        status=True,
    )
    
    # check is this person is qualified to see this pricing and event_price
    qualified_pricing = get_pricing(request.user, event, pricing=pricings)
    qualifies = False
    # custom registration form
    # use the custom registration form if pricing is associated with a custom reg form
    
    reg_conf=event.registration_configuration

    for q_price in qualified_pricing:
        if pricing.pk == q_price['price'].pk:
            qualifies = True
            
    if not qualifies:
        return multi_register_redirect(request, event, _('Please choose a price.'))
    
    # check if use a custom reg form
    custom_reg_form = None
    if reg_conf.use_custom_reg_form:
        if reg_conf.bind_reg_form_to_conf_only:
            custom_reg_form = reg_conf.reg_form
        else:
            custom_reg_form = pricing.reg_form

    # check if this post came from the pricing form
    # and modify the request method
    # we want it to fake a get here so that
    # the client can't actually see the pricing
    # var
    if 'from_price_form' in request.POST:
        request.method = 'GET'
        request.POST = QueryDict({})

    # check if it is still open based on dates
    reg_started = registration_has_started(event, pricing=pricings)
    if not reg_started:
        return multi_register_redirect(request, event, _('Registration has been closed.'))     

    # update the spots left
    limit = event.registration_configuration.limit
    spots_taken = 0
    if limit > 0:
        spots_taken = get_event_spots_taken(event)
        if spots_taken > limit:
            return multi_register_redirect(request, event, _('Registration is full.'))
    
    if custom_reg_form:
        RF = FormForCustomRegForm
    else:
        RF = RegistrantForm
    #RF = RegistrantForm
    
    # start the form set factory    
    RegistrantFormSet = formset_factory(
        RF,
        formset=RegistrantBaseFormSet,
        can_delete=True,
        max_num=pricing.quantity,
        extra=(pricing.quantity - 1)
    )
    
    # get available addons
    addons = get_available_addons(event, request.user)
    
    # start addon formset factory
    RegAddonFormSet = formset_factory(
        RegAddonForm,
        formset=RegAddonBaseFormSet,
        extra=0,
    )
    
    # update the amount of forms based on quantity
    total_regt_forms = pricing.quantity
    
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
        
        params = {'prefix': 'registrant',
                  'initial': [initial],
                  'event': event}
        if custom_reg_form:
            params.update({"custom_reg_form": custom_reg_form})
        
        registrant = RegistrantFormSet(**params)
        
        addon_formset = RegAddonFormSet(
                            prefix='addon',
                            event=event,
                            extra_params={
                                'addons':addons,
                            })
        
    else: 
        if post_data and 'add_registrant' in request.POST:
            post_data = request.POST.copy()
            post_data['registrant-TOTAL_FORMS'] = int(post_data['registrant-TOTAL_FORMS'])+ 1 
            
        params = {'prefix': 'registrant',
                  'event': event}
        if custom_reg_form:
            params.update({"custom_reg_form": custom_reg_form}) 
        registrant = RegistrantFormSet(post_data, **params)
        addon_formset = RegAddonFormSet(request.POST,
                            prefix='addon',
                            event=event,
                            extra_params={
                                'addons':addons,
                                'valid_addons':addons,
                            })
                            
    # REGISTRATION form
    if request.method == 'POST' and 'submit' in request.POST:
        reg_form = RegistrationForm(
            event,
            pricing,
            event_price,
            request.POST, 
            user=request.user,
            count=len(registrant.forms),
        )
    else:
        reg_form = RegistrationForm(
            event,
            pricing,
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
            if False not in (reg_form.is_valid(), registrant.is_valid(), addon_formset.is_valid()):
                
                # override event_price to price specified by admin
                admin_notes = ''
                if is_admin(request.user) and event_price > 0:
                    if event_price != reg_form.cleaned_data['amount_for_admin']:
                        admin_notes = "Price has been overriden for this registration. "
                    event_price = reg_form.cleaned_data['amount_for_admin']
                    
                reg8n, reg8n_created = add_registration(
                    request, 
                    event, 
                    reg_form, 
                    registrant,
                    addon_formset,
                    pricing,
                    event_price,
                    admin_notes=admin_notes,
                    custom_reg_form=custom_reg_form,
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
                    registrants = reg8n.registrant_set.all().order_by('id')
                    for registrant in registrants:
                        #registrant.assign_mapped_fields()
                        if registrant.custom_reg_form_entry:
                            registrant.name = registrant.custom_reg_form_entry.__unicode__()
                        else:
                            registrant.name = ' '.join([registrant.first_name, registrant.last_name])

                    if is_credit_card_payment:
                        # online payment
                        # get invoice; redirect to online pay
                        # email the admins as well
                        email_admins(event, event_price, self_reg8n, reg8n, registrants)
                        
                        return HttpResponseRedirect(reverse(
                            'payments.views.pay_online',
                            args=[reg8n.invoice.id, reg8n.invoice.guid]
                        )) 
                    else:
                        # offline payment:
                        # send email; add message; redirect to confirmation
                        primary_registrant = reg8n.registrant
                        
                        if primary_registrant and  primary_registrant.email:
                            notification.send_emails(
                                [primary_registrant.email],
                                'event_registration_confirmation',
                                {   
                                    'SITE_GLOBAL_SITEDISPLAYNAME': site_label,
                                    'SITE_GLOBAL_SITEURL': site_url,
                                    'self_reg8n': self_reg8n,
                                    'reg8n': reg8n,
                                    'registrants': registrants,
                                    'event': event,
                                    'price': event_price,
                                    'is_paid': reg8n.invoice.balance == 0
                                 },
                                True, # save notice in db
                            )                            
                            #email the admins as well
                            email_admins(event, event_price, self_reg8n, reg8n, registrants)
                        
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
    
    # total price calculation when invalid
    for form in registrant.forms:
        deleted = False
        if form.data.get('registrant-%d-DELETE' % count, False):
            deleted = True
        if count % pricing.quantity == 0:
            price_list.append({'price': event_price, 'deleted':deleted})
        else:
            price_list.append({'price': 0.00 , 'deleted':deleted})
        if not deleted:
            if pricing.quantity > 1:
                total_price = event_price
            else:
                total_price += event_price
        count += 1
    addons_price = addon_formset.get_total_price()
    total_price += addons_price
    
    # check if we have any error on registrant formset
    has_registrant_form_errors = False
    for form in registrant.forms:
        for field in form:
            if field.errors:
                has_registrant_form_errors = True
                break
        if has_registrant_form_errors:
            break
    return render_to_response(template_name, {
        'event':event,
        'event_price': event_price,
        'free_event': free_event,
        'price_list':price_list,
        'total_price':total_price,
        'price': pricing,
        'reg_form':reg_form,
        'custom_reg_form': custom_reg_form,
        'registrant': registrant,
        'addons':addons,
        'addon_formset': addon_formset,
        'total_regt_forms': total_regt_forms,
        'has_registrant_form_errors': has_registrant_form_errors,
    }, context_instance=RequestContext(request))
    
    
def registration_edit(request, reg8n_id=0, hash='', template_name="events/reg8n/reg8n_edit.html"):
    reg8n = get_object_or_404(Registration, pk=reg8n_id)

    perms = (
        has_perm(request.user, 'events.change_registration', reg8n),  # has perm
        request.user == reg8n.registrant.user,  # main registrant
        reg8n.registrant.hash == hash,  # has secret hash
    )

    if not any(perms):
        raise Http403
    
    custom_reg_form = None
    reg_conf = reg8n.event.registration_configuration
    if reg_conf.use_custom_reg_form:
        if reg_conf.bind_reg_form_to_conf_only:
            custom_reg_form = reg_conf.reg_form
        else:
            custom_reg_form = reg8n.reg_conf_price.reg_form
    
    if custom_reg_form:
        # use formset_factory for custom registration form
        RegistrantFormSet = formset_factory(
            FormForCustomRegForm, 
            formset=RegistrantBaseFormSet,
            max_num=reg8n.registrant_set.filter(registration=reg8n).count(),
            extra=0
        )
        entry_ids = reg8n.registrant_set.values_list('custom_reg_form_entry', flat=True).order_by('id')
        entries = [CustomRegFormEntry.objects.get(id=id) for id in entry_ids]
        params = {'prefix': 'registrant',
                  'custom_reg_form': custom_reg_form,
                  'entries': entries,
                  'event': reg8n.event}
        if request.method != 'POST':
            # build initial
            params.update({'initial': get_custom_registrants_initials(entries),})
        formset = RegistrantFormSet(request.POST or None, **params)
    else:
        # use modelformset_factory for regular registration form
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
            updated = False
            if custom_reg_form:
                for form in formset.forms:
                    form.save(reg8n.event)
                updated = True
            else:
                instances = formset.save()
                if instances: updated = True
            
            reg8n_conf_url = reverse( 
                                    'event.registration_confirmation',
                                    args=(reg8n.event.id, reg8n.registrant.hash)
                                    )
        
            if updated:
            
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


    perms = (
        has_perm(request.user, 'events.change_registration', registration),  # has perm
        request.user == registration.registrant.user,  # main registrant
        registration.registrant.hash == hash,  # has secret hash
    )

    if not any(perms):
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
                    if invoice and not invoice.is_tendered:
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
            args=[event.pk, registration.registrant.hash])
        )
        
    for regt in registrants:
        if regt.custom_reg_form_entry:
            regt.assign_mapped_fields()
            if not regt.name:
                regt.last_name = regt.name = regt.custom_reg_form_entry.__unicode__()
    for c_regt in cancelled_registrants:
        if c_regt.custom_reg_form_entry:
            c_regt.assign_mapped_fields()
            if not regt.name:
                regt.last_name = regt.name = regt.custom_reg_form_entry.__unicode__()
        
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
        sqs = Registrant.objects.filter(registration__event=event)
        sqs = sqs.order_by("-update_dt")

        # if the for loop is heavy, add the hash field to the table Registrant
        registrant = None
        for reg in sqs:
            if reg.hash == hash:
                registrant = reg
                break
        if not registrant:
            raise Http404

    if registrant.cancel_dt:
        raise Http404

    if request.method == "POST":
        # check if already canceled. if so, do nothing
        if not registrant.cancel_dt:
            user_is_registrant = False
            if request.user.is_authenticated() and registrant.user:
                if request.user == registrant.user:
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
        
    if registrant.custom_reg_form_entry:
        registrant.assign_mapped_fields()
        if not registrant.name:
            registrant.last_name = registrant.name = registrant.custom_reg_form_entry.__unicode__()
           
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
        if not Type.objects.filter(slug=type).exists():
            return HttpResponseRedirect(reverse('event.month'))

    # default/convert month and year
    if month and year:
        month, year = int(month), int(year)
    else:
        month, year = datetime.now().month, datetime.now().year
    
    if year <= 1900 or year >= 9999:
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
    if year <= 1900:
        raise Http404
    
    return render_to_response(template_name, {
        'date': datetime(year=int(year), month=int(month), day=int(day)),
        'now':datetime.now(),
        'type':None,
    }, context_instance=RequestContext(request))

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
    
    if not has_perm(request.user,'events.change_event', event):
        raise Http403
            
    if not query:
        # pull directly from db
        sqs = Registrant.objects.filter(registration__event=event)
        registrants = sqs.order_by("-update_dt")
        active_registrants = sqs.filter(cancel_dt=None).order_by("-update_dt")
        canceled_registrants = sqs.exclude(cancel_dt=None).order_by("-update_dt")
    else:
        sqs = SearchQuerySet().models(Registrant).filter(event_pk=event.id)
        sqs = sqs.auto_query(sqs.query.clean(query))
        registrants = sqs.order_by("-update_dt")
        active_registrants = sqs.auto_query(sqs.query.clean("is:active")).order_by("-update_dt")
        canceled_registrants = sqs.auto_query(sqs.query.clean("is:canceled")).order_by("-update_dt")
        
    
            
    for reg in registrants:
        if hasattr(reg, 'object'): reg = reg.object
        if reg.custom_reg_form_entry:
            reg.assign_mapped_fields()
            reg.non_mapped_field_entries = reg.custom_reg_form_entry.get_non_mapped_field_entry_list()
            if not reg.name:
                reg.name = reg.custom_reg_form_entry.__unicode__()
    for reg in active_registrants:
        if hasattr(reg, 'object'): reg = reg.object
        if reg.custom_reg_form_entry:
            reg.assign_mapped_fields()
            reg.non_mapped_field_entries = reg.custom_reg_form_entry.get_non_mapped_field_entry_list()
            if not reg.name:
                reg.name = reg.custom_reg_form_entry.__unicode__()
    for reg in canceled_registrants:
        if hasattr(reg, 'object'): reg = reg.object
        if reg.custom_reg_form_entry:
            reg.assign_mapped_fields()
            reg.non_mapped_field_entries = reg.custom_reg_form_entry.get_non_mapped_field_entry_list()
            if not reg.name:
                reg.name = reg.custom_reg_form_entry.__unicode__()

    return render_to_response(template_name, {
        'event':event, 
        'registrants':registrants,
        'active_registrants':active_registrants,
        'canceled_registrants':canceled_registrants,
        'query': query,
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
    for registrant in primary_registrants:
        if registrant.custom_reg_form_entry:
            registrant.assign_mapped_fields()
            registrant.roster_field_list =registrant.custom_reg_form_entry.roster_field_entry_list()
            if not registrant.name:
                registrant.last_name = registrant.__unicode__()
    primary_registrants = sorted(primary_registrants, key=lambda reg: reg.last_name)
    
    registrants = []
    for primary_reg in primary_registrants:
        registrants.append(primary_reg)
        for reg in primary_reg.additional_registrants:
            if reg.custom_reg_form_entry:
                reg.assign_mapped_fields()
                reg.roster_field_list =reg.custom_reg_form_entry.roster_field_entry_list()
                if not reg.name:
                    reg.last_name = reg.custom_reg_form_entry.__unicode__()
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
    """
    Registration information.
    Any registrant (belonging to this registration) 
    or administrator can see the entire registration.
    """

    event = get_object_or_404(Event, pk=id)
    registrants_count = 1
    registrant_hash = hash
    
    if reg8n_id:
        registration = get_object_or_404(Registration, event=event, pk=reg8n_id)
    
        is_permitted = has_perm(request.user, 'events.view_registration', registration)
        is_registrant = request.user in [r.user for r in registration.registrant_set.all()]

        # permission denied; if not given explicit permission or not registrant
        if not any((is_permitted, is_registrant)):
            raise Http403

        registrant = registration.registrant

    elif registrant_hash:
        # not real time index, pull directly from db
        #sqs = SearchQuerySet()
        #sqs = sqs.models(Registrant)
        #sqs = sqs.filter(event_pk=event.pk)
        #sqs = sqs.auto_query(sqs.query.clean(registrant_hash))
        sqs = Registrant.objects.filter(registration__event=event)
        sqs = sqs.order_by("-update_dt")
        
        # find the match - the for loop might be heavy. maybe add hash field later
        registrant = None
        for reg in sqs:
            if reg.hash == registrant_hash:
                registrant = reg
                break
        if not registrant:
            raise Http404

        try:
            #registrant = sqs[0].object
            registration = registrant.registration
        except:
            raise Http404

    registrants = registration.registrant_set.all().order_by('id')
    registrants_count = registration.registrant_set.count()
    addons = registration.regaddon_set.all().order_by('id')
    
    for registrant in registrants:
        #registrant.assign_mapped_fields()
        if registrant.custom_reg_form_entry:
            registrant.name = registrant.custom_reg_form_entry.__unicode__()
        else:
            registrant.name = ' '.join([registrant.first_name, registrant.last_name])
    
    return render_to_response(template_name, {
        'event':event,
        'registrant':registrant,
        'registration':registration,
        'registrants': registrants,
        'registrants_count': registrants_count,
        'addons': addons,
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
            
            messages.add_message(request, messages.SUCCESS, 'Successfully sent email "%s" to event registrants for event "%s".' % (subject, event.title))
            
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


def registrant_export_with_custom(request, event_id, roster_view=''):
    """
    Export all registration for a specific event with or without custom registration forms
    """
    from django.db import connection
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
    
        # excel date styles
    styles = {
        'balance_owed_style': xlwt.easyxf('font: color-index red, bold on'),
        'default_style': xlwt.Style.default_style,
        'datetime_style': xlwt.easyxf(num_format_str='mm/dd/yyyy hh:mm'),
        'date_style': xlwt.easyxf(num_format_str='mm/dd/yyyy')
    }

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
        ('company', 'company_name'),
        ('address', 'address'),
        ('city', 'city'),
        ('state', 'state'),
        ('zip', 'zip'),
        ('country', 'country'),
        ('date', 'create_dt'),
        ('registration_id', 'registration__pk'),
        ('price type', 'registration__reg_conf_price__title'),
        ('invoice_id', 'registration__invoice__pk'),
        ('registration price', 'registration__amount_paid'),
        ('payment method', 'registration__payment_method__machine_name'),
        ('balance', 'registration__invoice__balance'),
    ])
    registrant_lookups = registrant_mappings.values()

    # Append the heading to the list of values that will
    # go into the excel sheet
    values_list = []

    # registrants with regular reg form
    non_custom_registrants = registrants.filter(custom_reg_form_entry=None)
    non_custom_registrants = non_custom_registrants.values_list(*registrant_lookups)
    if non_custom_registrants:
        values_list.insert(0, registrant_mappings.keys())
        for registrant in non_custom_registrants:
            values_list.append(registrant)
        values_list.append(['\n'])

    # Write the data enumerated to the excel sheet
    balance_index = 16
    start_row = 0
    render_registrant_excel(sheet, values_list, balance_index, styles, start=start_row)
    start_row += len(values_list)
            
    # ***now check for the custom registration forms***
    custom_reg_exists = Registrant.objects.filter(
                                    registration__event=event
                                    ).exclude(custom_reg_form_entry=None
                                              ).exists()

    if custom_reg_exists:
        # get a list of custom registration forms
        sql = """
            SELECT form_id 
            FROM events_customregformentry 
            WHERE id IN ( 
                SELECT custom_reg_form_entry_id 
                FROM events_registrant 
                WHERE (custom_reg_form_entry_id is not NULL) 
                AND registration_id IN ( 
                    SELECT id FROM events_registration 
                    WHERE event_id=%d))
            ORDER BY id
        """  % event.id
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        # list of form ids
        form_ids = list(set([row[0] for row in rows]))
        
        # remove some fields from registrant_mappings because they are
        # stored in the field entries
        fields_to_remove = ['first_name', 'last_name', 'phone', 
                            'email', 'company', 'address', 'city', 
                            'state', 'zip', 'country']
        for field in fields_to_remove:
            del registrant_mappings[field]
        
       
        registrant_lookups = registrant_mappings.values()
        registrant_lookups.append('custom_reg_form_entry')
        
        # loop through all custom registration forms
        for form_id in form_ids:
            rows_list = []
            custom_reg_form = CustomRegForm.objects.get(id=form_id)
            
            # get a list of fields in the type (id, label) and store in 
            # an ordered dict
            fields = CustomRegField.objects.filter(form=custom_reg_form
                                                   ).order_by(
                                                    'position'
                                                    ).values_list('id', 'label')
            fields_dict = OrderedDict(fields)
            field_ids = fields_dict.keys()
            # field header row - all the field labels in the form + registrant_mappings.keys
            labels = fields_dict.values()
            labels.extend(registrant_mappings.keys())
            
            rows_list.append([custom_reg_form.name])
            rows_list.append(labels)
            
            # get the registrants for this form
            custom_registrants = registrants.filter(custom_reg_form_entry__form=custom_reg_form)
            custom_registrants = custom_registrants.values_list(*registrant_lookups)
            for registrant in custom_registrants:
                entry_id = registrant[-1]
                sql = """
                        SELECT field_id, value
                        FROM events_customregfieldentry
                        WHERE field_id IN (%s)
                        AND entry_id=%d
                    """ % (','.join([str(id) for id in field_ids]), entry_id)
                cursor.execute(sql)
                entry_rows = cursor.fetchall()
                values_dict = dict(entry_rows)
                
                custom_values_list = []
                for field_id in field_ids:
                    custom_values_list.append(values_dict.get(field_id, ''))
                custom_values_list.extend(list(registrant[:-1]))
                
                rows_list.append(custom_values_list)
            rows_list.append(['\n'])
            
            balance_index =  len(field_ids) + len(registrant_lookups) - 1
            
            # write to spread sheet
            render_registrant_excel(sheet, rows_list, balance_index, styles, start=start_row)
            start_row += len(rows_list)
             

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
    
    messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % speaker)
    
    speaker.delete()
    
    return redirect('event', id=event.id)
    
@login_required
def delete_group_pricing(request, id):
    if not has_perm(request.user,'events.delete_registrationconfiguration'): 
        raise Http403
        
    gp = get_object_or_404(GroupRegistrationConfiguration, id = id)
    event = Event.objects.get(registration_configuration=gp.config)
    
    messages.add_message(request, messages.SUCCESS, 'Successfully deleted Group Pricing for %s' % gp)
    
    gp.delete()
    
    return redirect('event', id=event.id)
    
@login_required
def delete_special_pricing(request, id):
    if not has_perm(request.user,'events.delete_registrationconfiguration'): 
        raise Http403
        
    s = get_object_or_404(SpecialPricing, id = id)
    event = Event.objects.get(registration_configuration=s.config)
    
    messages.add_message(request, messages.SUCCESS, 'Successfully deleted Special Pricing for %s' % s)
    
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
    
    messages.add_message(request, messages.SUCCESS, 'Sucessfully copied Event: %s.<br />Edit the new event (set to <strong>private</strong>) below.' % new_event.title)
    
    return redirect('event.edit', id=new_event.id)
    
@login_required
def minimal_add(request, form_class=PendingEventForm, template_name="events/minimal_add.html"):
    """
    Minimal add for events. Events created here require admin approval.
    This does not require users to have the add_event permission.
    The minimaladdform setting must be enabled for this form to be active.
    """
    # check if this form is enabled for use.
    active = get_setting('module', 'events', 'minimaladdform')
    # raise 404 if form not active
    if not active:
        raise Http404
        
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, user=request.user, prefix="event")
        form_place = PlaceForm(request.POST, prefix="place")
        
        if form.is_valid() and form_place.is_valid():
            event = form.save(commit=False)
            
            # update all permissions and save the model
            event = update_perms_and_save(request, form, event)
            
            # save place
            place = form_place.save()
            event.place = place
            
            # place event into pending queue
            event.status = False
            event.status_detail = 'pending'
            event.save()
            
            # save photo
            photo = form.cleaned_data['photo_upload']
            if photo: event.save(photo=photo)
            
            messages.add_message(request, messages.SUCCESS,
                'Your event submission has been received. It is now subject to approval.')
            return redirect('events')
        print "form", form.errors
        print "form_place", form_place.errors
    else:
        form = form_class(user=request.user, prefix="event")
        form_place = PlaceForm(prefix="place")
        
    return render_to_response(template_name, {
        'form': form,
        'form_place': form_place,
        }, context_instance=RequestContext(request))

@login_required
def pending(request, template_name="events/pending.html"):
    """
    Show a list of pending events to be approved.
    """
    if not is_admin(request.user):
        raise Http403
        
    events = Event.objects.filter(status=False, status_detail='pending').order_by('start_dt')
    
    return render_to_response(template_name, {
        'events': events,
        }, context_instance=RequestContext(request))

@login_required
def approve(request, event_id, template_name="events/approve.html"):
    """
    Approve a selected event
    """
    
    if not is_admin(request.user):
        raise Http403
    
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == "POST":
        event.status = True
        event.status_detail = 'active'
        event.save()
        
        messages.add_message(request, messages.SUCCESS, 'Successfully approved %s' % event)
        
        return redirect('event', id=event_id)
    
    return render_to_response(template_name, {
        'event': event,
        }, context_instance=RequestContext(request))

@login_required
def list_addons(request, event_id, template_name="events/addons/list.html"):
    """List addons of an event"""
    
    event = get_object_or_404(Event, pk=event_id)
    
    if not has_view_perm(request.user,'events.view_event', event):
        raise Http404
    
    return render_to_response(template_name, {
        'event':event,
        'addons':event.addon_set.all(),
    }, context_instance=RequestContext(request))

@login_required
def add_addon(request, event_id, template_name="events/addons/add.html"):
    """Add an addon for an event"""
    event = get_object_or_404(Event, pk=event_id)
    
    if not has_perm(request.user,'events.change_event', event):
        raise Http404
        
    OptionFormSet = modelformset_factory(AddonOption, form=AddonOptionForm, extra=3)
    
    if request.method == "POST":
        form = AddonForm(request.POST)
        formset = OptionFormSet(request.POST, queryset=AddonOption.objects.none(), prefix="options")
        if False not in (form.is_valid(), formset.is_valid()):
            addon = form.save(commit=False)
            addon.event = event
            addon.save()
            
            options = formset.save(commit=False)
            for option in options:
                option.addon = addon
                option.save()
                
            messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % addon)
            return redirect('event', event.pk)
    else:
        form = AddonForm()
        formset = OptionFormSet(queryset=Addon.objects.none(), prefix="options")
        
    return render_to_response(template_name, {
        'form': form,
        'formset': formset,
        'event':event,
    }, context_instance=RequestContext(request))    

@login_required
def edit_addon(request, event_id, addon_id, template_name="events/addons/edit.html"):
    """Edit addon for an event"""
    event = get_object_or_404(Event, pk=event_id)
    
    if not has_perm(request.user,'events.change_event', event):
        raise Http404
    
    addon = get_object_or_404(Addon, pk=addon_id)
    
    OptionFormSet = inlineformset_factory(Addon, AddonOption, form=AddonOptionForm, extra=3)
    
    if request.method == "POST":
        form = AddonForm(request.POST, instance=addon)
        formset = OptionFormSet(request.POST, instance=addon, prefix="options")
        if False not in (form.is_valid(), formset.is_valid()):
            addon = form.save()
            options = formset.save()
            
            messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % addon)
            return redirect('event', event.pk)
    else:
        form = AddonForm(instance=addon)
        formset = OptionFormSet(instance=addon, prefix="options")
        
    return render_to_response(template_name, {
        'formset':formset,
        'form':form,
        'event':event,
    }, context_instance=RequestContext(request))
    
@login_required
def disable_addon(request, event_id, addon_id):
    """delete addon for an event"""
    event = get_object_or_404(Event, pk=event_id)
    
    if not has_perm(request.user,'events.change_event', event):
        raise Http404
    
    addon = get_object_or_404(Addon, pk=addon_id)
    addon.delete() # this just renders it inactive to not cause deletion of already existing regaddons
    messages.add_message(request, messages.SUCCESS, "Successfully disabled the %s" % addon.title)
        
    return redirect('event.list_addons', event.id)

@login_required
def enable_addon(request, event_id, addon_id):
    """delete addon for an event"""
    event = get_object_or_404(Event, pk=event_id)
    
    if not has_perm(request.user,'events.change_event', event):
        raise Http404
    
    addon = get_object_or_404(Addon, pk=addon_id)
    addon.status = True
    addon.save()
    messages.add_message(request, messages.SUCCESS, "Successfully enabled the %s" % addon.title)
        
    return redirect('event.list_addons', event.id)
