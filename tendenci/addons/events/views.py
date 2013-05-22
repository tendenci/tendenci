# NOTE: When updating the registration scheme be sure to check with the
# anonymous registration impementation of events in the registration
# module.

import os
import re
import time
import calendar
import itertools
import cPickle
import threading
import subprocess

from datetime import datetime
from datetime import date, timedelta
from decimal import Decimal
from haystack.query import SearchQuerySet

from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson as json
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.http import QueryDict
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage
from django.contrib import messages
from django.template.loader import render_to_string
from django.template.defaultfilters import date as date_filter
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory, \
    inlineformset_factory
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson as json
from django.db import connection

from tendenci.core.base.http import Http403
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.decorators import is_enabled
from tendenci.core.perms.utils import (has_perm, get_notice_recipients,
    get_query_filters, update_perms_and_save, has_view_perm)
from tendenci.core.event_logs.models import EventLog
from tendenci.core.meta.models import Meta as MetaTags
from tendenci.core.meta.forms import MetaForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from tendenci.core.files.models import File
from tendenci.core.theme.shortcuts import themed_response as render_to_response
from tendenci.core.exports.utils import run_export_task
from tendenci.core.imports.forms import ImportForm
from tendenci.core.imports.models import Import
from tendenci.core.base.decorators import password_required
from tendenci.core.base.utils import convert_absolute_urls
from tendenci.core.imports.utils import (extract_from_excel,
                render_excel)

from tendenci.apps.discounts.models import Discount
from tendenci.apps.notifications import models as notification
from tendenci.addons.events.ics.utils import run_precreate_ics

from tendenci.addons.events.models import (Event,
    Registration, Registrant, Speaker, Organizer, Type,
    RegConfPricing, Addon, AddonOption, CustomRegForm,
    CustomRegFormEntry, CustomRegField, CustomRegFieldEntry,
    RegAddonOption, RegistrationConfiguration, EventPhoto, Place)
from tendenci.addons.events.forms import (EventForm, Reg8nEditForm,
    PlaceForm, SpeakerForm, OrganizerForm, TypeForm, MessageAddForm,
    RegistrationForm, RegistrantForm, RegistrantBaseFormSet,
    Reg8nConfPricingForm, PendingEventForm, AddonForm, AddonOptionForm,
    FormForCustomRegForm, RegConfPricingBaseModelFormSet, RegistrantSearchForm,
    RegistrationPreForm, EventICSForm, EmailForm, DisplayAttendeesForm, ReassignTypeForm)
from tendenci.addons.events.utils import (email_registrants,
    render_event_email, get_default_reminder_template,
    add_registration, registration_has_started, registration_has_ended,
    registration_earliest_time, get_pricing, clean_price,
    get_event_spots_taken, get_ievent, split_table_price,
    copy_event, email_admins, get_active_days, get_ACRF_queryset,
    get_custom_registrants_initials, render_registrant_excel,
    event_import_process, check_month)
from tendenci.addons.events.addons.forms import RegAddonForm
from tendenci.addons.events.addons.formsets import RegAddonBaseFormSet
from tendenci.addons.events.addons.utils import get_available_addons
from tendenci.core.base.utils import convert_absolute_urls
from tendenci.apps.redirects.models import Redirect


def custom_reg_form_preview(request, id,
        template_name="events/custom_reg_form_preview.html"):
    """
    Preview a custom registration form.
    """
    form = get_object_or_404(CustomRegForm, id=id)

    form_for_form = FormForCustomRegForm(request.POST or None,
        request.FILES or None, custom_reg_form=form, user=request.user)

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
    if not has_perm(request.user, 'events.change_event', event):
        raise Http403

    reg_conf = event.registration_configuration
    regconfpricings = reg_conf.regconfpricing_set.all()

    if reg_conf.use_custom_reg_form:
        if reg_conf.bind_reg_form_to_conf_only:
            reg_conf.reg_form.form_for_form = FormForCustomRegForm(
                custom_reg_form=reg_conf.reg_form)
        else:
            for price in regconfpricings:
                price.reg_form.form_for_form = FormForCustomRegForm(custom_reg_form=price.reg_form)

    context = {
        'event': event,
        'reg_conf': reg_conf,
        'regconfpricings': regconfpricings
    }

    return render_to_response(template_name, context, RequestContext(request))


@is_enabled('events')
def details(request, id=None, template_name="events/view.html"):
    if not id:
        return HttpResponseRedirect(reverse('event.month'))

    event = get_object_or_404(Event, pk=id)

    days = []
    if not event.on_weekend:
        days = get_active_days(event)

    if not has_view_perm(request.user, 'events.view_event', event):
        raise Http403

    if event.registration_configuration:
        event.limit = event.get_limit()
    else:
        reg_conf = RegistrationConfiguration()
        reg_conf.save()
        event.registration_configuration = reg_conf
        event.save()

    event.spots_taken, event.spots_available = event.get_spots_status()

    EventLog.objects.log(instance=event)

    speakers = event.speaker_set.all().order_by('pk')
    organizers = event.organizer_set.all().order_by('pk') or None

    organizer = None
    if organizers:
        organizer = organizers[0]

    return render_to_response(template_name, {
        'days': days,
        'event': event,
        'speakers': speakers,
        'organizer': organizer,
        'now': datetime.now(),
        'addons': event.addon_set.filter(status=True),
    }, context_instance=RequestContext(request))


@is_enabled('events')
def view_attendees(request, event_id, template_name='events/attendees.html'):
    event = get_object_or_404(Event, pk=event_id)

    if not event.can_view_registrants(request.user):
        raise Http403

    limit = event.get_limit()
    registration = event.registration_configuration

    pricing = registration.get_available_pricings(request.user, is_strict=False)
    pricing = pricing.order_by('position', '-price')

    reg_started = registration_has_started(event, pricing=pricing)
    reg_ended = registration_has_ended(event, pricing=pricing)
    earliest_time = registration_earliest_time(event, pricing=pricing)

    # spots taken
    if limit > 0:
        slots_taken, slots_available = event.get_spots_status()
    else:
        slots_taken, slots_available = (-1, -1)

    is_registrant = False
    # check if user has already registered
    if hasattr(request.user, 'registrant_set'):
        is_registrant = request.user.registrant_set.filter(registration__event=event).exists()

    return render_to_response(template_name, {
        'event': event,
        'registration': registration,
        'limit': limit,
        'slots_taken': slots_taken,
        'slots_available': slots_available,
        'reg_started': reg_started,
        'reg_ended': reg_ended,
        'earliest_time': earliest_time,
        'is_registrant': is_registrant,
    }, context_instance=RequestContext(request))


def month_redirect(request):
    return HttpResponseRedirect(reverse('event.month'))


@is_enabled('events')
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
    with_registration = request.GET.get('registration', None)
    try:
        start_dt = datetime.strptime(start_dt, '%Y-%m-%d')
    except:
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
        if event_type:
            events = events.filter(type__slug=event_type,
                end_dt__gte=start_dt)
        else:
            events = events.filter(start_dt__gte=start_dt)
        if request.user.is_authenticated():
            events = events.select_related()

    if with_registration:
        events = events.filter(registration_configuration__enabled=True)

    events = events.order_by('start_dt', '-priority')

    types = Type.objects.all().order_by('name')

    EventLog.objects.log()

    return render_to_response(template_name, {
        'events': events,
        'types': types,
        'now': datetime.now(),
        'event_type': event_type,
        'start_dt': start_dt,
        'with_registration': with_registration,
        }, context_instance=RequestContext(request))


def icalendar(request):
    import os
    from tendenci.settings import MEDIA_ROOT
    from tendenci.addons.events.utils import get_vevents
    p = re.compile(r'http(s)?://(www.)?([^/]+)')
    d = {}
    file_name = ''
    ics_str = ''

    d['site_url'] = get_setting('site', 'global', 'siteurl')
    match = p.search(d['site_url'])
    if match:
        d['domain_name'] = match.group(3)
    else:
        d['domain_name'] = ""

    if request.user.is_authenticated():
        file_name = 'ics-%s.ics' % (request.user.pk)

    absolute_directory = os.path.join(MEDIA_ROOT, 'files/ics')
    if not os.path.exists(absolute_directory):
        os.makedirs(absolute_directory)

    if file_name:
        file_path = os.path.join(absolute_directory, file_name)
        # Check if ics file exists
        if os.path.isfile(file_path):
            ics = open(file_path, 'r+')
            ics_str = ics.read()
            ics.close()
    if not ics_str:
        ics_str = "BEGIN:VCALENDAR\n"
        ics_str += "PRODID:-//Schipul Technologies//Schipul Codebase 5.0 MIMEDIR//EN\n"
        ics_str += "VERSION:2.0\n"
        ics_str += "METHOD:PUBLISH\n"

        # function get_vevents in events.utils
        ics_str += get_vevents(request.user, d)

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
    from tendenci.addons.events.utils import get_vevents
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
    ics_str += get_ievent(request.user, d, id)

    ics_str += "END:VCALENDAR\n"

    response = HttpResponse(ics_str)
    response['Content-Type'] = 'text/calendar'
    if d['domain_name']:
        file_name = '%s.ics' % (d['domain_name'])
    else:
        file_name = "event.ics"
    response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
    return response


@is_enabled('events')
def print_view(request, id, template_name="events/print-view.html"):
    event = get_object_or_404(Event, pk=id)

    if has_view_perm(request.user,'events.view_event',event):
        EventLog.objects.log(instance=event)

        return render_to_response(template_name, {'event': event},
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('events')
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

    if event.registration_configuration and\
             event.registration_configuration.regconfpricing_set.all():
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
            form_attendees = DisplayAttendeesForm(request.POST)

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
                form_attendees,
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
                event.display_event_registrants = form_attendees.cleaned_data['display_event_registrants']
                event.display_registrants_to = form_attendees.cleaned_data['display_registrants_to']

                # update all permissions and save the model
                event = update_perms_and_save(request, form_event, event)

                # handle image
                f = form_event.cleaned_data['photo_upload']
                if f:
                    image = EventPhoto()
                    image.object_id = event.id
                    image.creator = request.user
                    image.creator_username = request.user.username
                    image.owner = request.user
                    image.owner_username = request.user.username
                    filename = "%s-%s" % (event.id, f.name)
                    f.file.seek(0)
                    image.file.save(filename, f)
                    event.image = image

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
                event.save(log=False)

                # un-tie the reg_form from the pricing
                if not pricing_reg_form_required:
                    for price in regconf.regconfpricing_set.all():
                        if price.reg_form:
                            price.reg_form = None
                            price.save()

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
            form_attendees = DisplayAttendeesForm(
                initial={
                    'display_event_registrants':event.display_event_registrants,
                    'display_registrants_to':event.display_registrants_to,
                }
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
                form_attendees,
                form_regconfpricing
                ],
            },
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('events')
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


@csrf_exempt
def get_place(request):
    if request.method == 'POST':
        place_id = request.POST.get('id', None)
        if place_id:
            try:
                place = Place.objects.get(pk=place_id)
                return HttpResponse(json.dumps(
                {
                    "error": False,
                    "message": "Get place success.",
                    "name": place.name,
                    "description": place.description,
                    "address": place.address,
                    "city": place.city,
                    "state": place.state,
                    "zip": place.zip,
                    "country": place.country,
                    "url": place.url,
                }), mimetype="text/plain")
            except Place.DoesNotExist:
                return HttpResponse(json.dumps({
                    "error": True,
                    "message": "Place does not exist.",
                }), mimetype="text/plain")

        return HttpResponse(json.dumps(
            {
                "error": True,
                "message": "No id provided.",
            }), mimetype="text/plain")

    return HttpResponse('Requires POST method.')


@is_enabled('events')
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
            form_attendees = DisplayAttendeesForm(request.POST)

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
                form_attendees,
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
                event.display_event_registrants = form_attendees.cleaned_data['display_event_registrants']
                event.display_registrants_to = form_attendees.cleaned_data['display_registrants_to']

                # update all permissions and save the model
                event = update_perms_and_save(request, form_event, event)

                # handle image
                f = form_event.cleaned_data['photo_upload']
                if f:
                    image = EventPhoto()
                    image.object_id = event.id
                    image.creator = request.user
                    image.creator_username = request.user.username
                    image.owner = request.user
                    image.owner_username = request.user.username
                    filename = "%s-%s" % (event.id, f.name)
                    f.file.seek(0)
                    image.file.save(filename, f)
                    event.image = image

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
                event.save(log=False)

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

            # default to 30 days from now
            mydate = datetime.now()+timedelta(days=30)
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
                start_dt = mydate
                end_dt = start_dt + offset

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
            form_attendees = DisplayAttendeesForm()

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
                form_attendees,
                form_regconfpricing
                ],
            },
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('events')
@login_required
def delete(request, id, template_name="events/delete.html"):
    event = get_object_or_404(Event, pk=id)

    if has_perm(request.user, 'events.delete_event'):
        if request.method == "POST":

            eventlog = EventLog.objects.log(instance=event)
            # send email to admins
            recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
            if recipients and notification:
                notification.send_emails(recipients, 'event_deleted', {
                    'event': event,
                    'request': request,
                    'user': request.user,
                    'registrants_paid': event.registrants(with_balance=False),
                    'registrants_pending': event.registrants(with_balance=True),
                    'eventlog_url': reverse('event_log', args=[eventlog.pk]),
                    'SITE_GLOBAL_SITEDISPLAYNAME': get_setting('site', 'global', 'sitedisplayname'),
                    'SITE_GLOBAL_SITEURL': get_setting('site', 'global', 'siteurl'),
                })

            if event.image:
                event.image.delete()

            event.delete(log=False)

            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % event)

            return HttpResponseRedirect(reverse('event.search'))

        return render_to_response(template_name, {'event': event},
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('events')
def register_pre(request, event_id, template_name="events/reg8n/register_pre2.html"):
    event = get_object_or_404(Event, pk=event_id)

    reg_conf=event.registration_configuration
    anony_reg8n = get_setting('module', 'events', 'anonymousregistration')

    # check spots available
    limit = event.get_limit()
    spots_taken, spots_available = event.get_spots_status()

    if limit > 0 and spots_available == 0:
        if not request.user.profile.is_superuser:
            # is no more spots available, redirect to event view.
            return multi_register_redirect(request, event, _('Registration is full.'))
    event.limit, event.spots_taken, event.spots_available = limit, spots_taken, spots_available

    pricings = reg_conf.get_available_pricings(request.user,
                                               is_strict=False,
                                               spots_available=spots_available
                                               )

    individual_pricings = pricings.filter(quantity=1).order_by('position', '-price')
    table_pricings = pricings.filter(quantity__gt=1).order_by('position', '-price')

    if not (individual_pricings or table_pricings):
        raise Http404


    return render_to_response(template_name, {
        'event':event,
        'individual_pricings': individual_pricings,
        'table_pricings': table_pricings,
        'quantity_options': range(31)
    }, context_instance=RequestContext(request))



def multi_register_redirect(request, event, msg):
    messages.add_message(request, messages.INFO, msg)
    return HttpResponseRedirect(reverse('event', args=(event.pk,),))


@is_enabled('events')
def register(request, event_id=0,
             individual=False,
             is_table=False,
             pricing_id=None,
             template_name="events/reg8n/register.html"):
    """
    Handles both table and non-table registrations.
    Table registration requires is_table=True and a valid pricing_id.
    """
    event = get_object_or_404(Event, pk=event_id)

    # open,validated or strict
    anony_setting = get_setting('module', 'events', 'anonymousregistration')
    event.anony_setting = anony_setting
    is_strict = anony_setting == 'strict'

    if is_strict:
        # strict requires logged in
        if not request.user.is_authenticated():
            messages.add_message(request, messages.INFO,
                                 'Please log in or sign up to the site before registering the event.')
            return HttpResponseRedirect('%s?next=%s' % (reverse('auth_login'),
                                                        reverse('event.register', args=[event.id])))


    # check if event allows registration
    if not event.registration_configuration and \
       event.registration_configuration.enabled:
        raise Http404

    # check spots available
    limit = event.get_limit()
    spots_taken, spots_available = event.get_spots_status()

    if limit > 0 and spots_available == 0:
        if not request.user.profile.is_superuser:
            # is no more spots available, redirect to event view.
            return multi_register_redirect(request, event, _('Registration is full.'))
    event.limit, event.spots_taken, event.spots_available = limit, spots_taken, spots_available


    reg_conf=event.registration_configuration

    if not any((individual, is_table)):
        # Check if the event has both individual and table registrations.
        # If so, redirect them to the intermediate page to choose individual
        # or table.
        pricings = reg_conf.get_available_pricings(request.user,
                                                   is_strict=False,
                                                   spots_available=spots_available)
        if not pricings:
            raise Http404

        if len(pricings) > 1:
            return HttpResponseRedirect(reverse('event.register_pre', args=(event.pk,),))


        pricing = pricings[0]
        if pricing.quantity == 1:
            individual = True
            event.default_pricing = pricing
        else:
            is_table = True
            pricing_id = pricing.id

    else:
        pricings = None


    event.is_table = is_table


    event.require_guests_info = reg_conf.require_guests_info

    if is_table and pricing_id:
        pricing = get_object_or_404(RegConfPricing, pk=pricing_id)
        event.free_event = pricing.price <=0
    else:
        # get all available pricing for the Price Options to select
        if not pricings:
            pricings = reg_conf.get_available_pricings(request.user,
                                                       is_strict=False,
                                                       spots_available=spots_available)
        pricings = pricings.filter(quantity=1)

        event.has_member_price = pricings.filter(allow_member=True
                                                 ).exclude(
                                        Q(allow_user=True) | Q(allow_anonymous=True)
                                                ).exists()

        pricings = pricings.order_by('position', '-price')
        # registration might be closed, redirect to detail page
        if not pricings.exists():
            return HttpResponseRedirect(reverse('event', args=(event.pk,),))

        try:
            pricing_id = int(pricing_id)
        except:
            pass

        if pricing_id:
            [event.default_pricing] = RegConfPricing.objects.filter(id=pricing_id) or [None]

        event.free_event = not bool([p for p in pricings if p.price > 0])
        pricing = None


    # check if using a custom reg form
    custom_reg_form = None
    if reg_conf.use_custom_reg_form:
        if reg_conf.bind_reg_form_to_conf_only:
            custom_reg_form = reg_conf.reg_form


    if custom_reg_form:
        RF = FormForCustomRegForm
    else:
        RF = RegistrantForm
    #RF = RegistrantForm

    total_regt_forms = pricing and pricing.quantity or 1
    can_delete = (not is_table)
    # start the form set factory
    RegistrantFormSet = formset_factory(
        RF,
        formset=RegistrantBaseFormSet,
        can_delete=can_delete,
        max_num=total_regt_forms,
        extra=pricing and (pricing.quantity - 1) or 0
    )

    # get available addons
    addons = get_available_addons(event, request.user)
    # start addon formset factory
    RegAddonFormSet = formset_factory(
        RegAddonForm,
        formset=RegAddonBaseFormSet,
        extra=0,
    )

    # REGISTRANT formset
    post_data = request.POST or None

    params = {'prefix': 'registrant',
              'event': event,
              'user': request.user}
    if not is_table:
        # pass the pricings to display the price options
        params.update({'pricings': pricings})

    if custom_reg_form:
        params.update({"custom_reg_form": custom_reg_form})

    addon_extra_params = {'addons':addons}

    # Setting the initial or post data
    if request.method != 'POST':
        # set the initial data if logged in
        initial = {}
        if request.user.is_authenticated():
            profile = request.user.profile

            initial = {'first_name':request.user.first_name,
                        'last_name':request.user.last_name,
                        'email':request.user.email,}
            if profile:
                initial.update({'company_name': profile.company,
                                'phone':profile.phone,
                                'address': profile.address,
                                'city': profile.city,
                                'state': profile.state,
                                'zip': profile.zipcode,
                                'country': profile.country,
                                'position_title': profile.position_title})

        params.update({"initial": [initial]})

        post_data = None
    else:
        if post_data and 'add_registrant' in request.POST:
            post_data = request.POST.copy()
            post_data['registrant-TOTAL_FORMS'] = int(post_data['registrant-TOTAL_FORMS'])+ 1

        addon_extra_params.update({'valid_addons':addons})


    # check if we have any valid discount code for the event.
    # if not, we don't have to display the discount code box.
    if reg_conf.discount_eligible:
        reg_conf.discount_eligible = Discount.has_valid_discount(model=reg_conf._meta.module_name)

    # Setting up the formset
    registrant = RegistrantFormSet(post_data or None, **params)
    addon_formset = RegAddonFormSet(request.POST or None,
                        prefix='addon',
                        event=event,
                        extra_params=addon_extra_params)

    # REGISTRATION form
    reg_form = RegistrationForm(
            event,
            request.POST or None,
            user=request.user,
            count=len(registrant.forms),
        )

    # remove captcha for logged in user
    if request.user.is_authenticated():
        del reg_form.fields['captcha']

    # total registrant forms
    if post_data:
        total_regt_forms = post_data['registrant-TOTAL_FORMS']
    within_available_spots = True

    if request.method == 'POST':
        if 'submit' in request.POST:

            #if not request.user.profile.is_superuser:
            within_available_spots = event.limit==0 or event.spots_available >= int(total_regt_forms)

            if all([within_available_spots,
                    reg_form.is_valid(),
                    registrant.is_valid(),
                    addon_formset.is_valid()]):

                args = [request, event, reg_form, registrant, addon_formset,
                        pricing, pricing and pricing.price or 0]

                kwargs = {'admin_notes': '',
                          'custom_reg_form': custom_reg_form}
                # add registration
                reg8n, reg8n_created = add_registration(*args, **kwargs)

                site_label = get_setting('site', 'global', 'sitedisplayname')
                site_url = get_setting('site', 'global', 'siteurl')
                self_reg8n = get_setting('module', 'users', 'selfregistration')

                is_credit_card_payment = reg8n.payment_method and \
                (reg8n.payment_method.machine_name).lower() == 'credit-card' \
                and reg8n.invoice.balance > 0

                if reg8n_created:
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
                        email_admins(event, reg8n.invoice.total, self_reg8n, reg8n, registrants)

                        return HttpResponseRedirect(reverse(
                            'payment.pay_online',
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
                                    'total_amount': reg8n.invoice.total,
                                    'is_paid': reg8n.invoice.balance == 0
                                 },
                                True, # save notice in db
                            )
                            #email the admins as well
                            # fix the price
                            email_admins(event, reg8n.invoice.total, self_reg8n, reg8n, registrants)

                    # log an event
                    EventLog.objects.log(instance=event)

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
    total_price = Decimal('0')
    event_price = pricing and pricing.price or 0
    individual_price = event_price

    if is_table:
#        individual_price_first, individual_price = split_table_price(
#                                                event_price, pricing.quantity)
        individual_price_first, individual_price = event_price, Decimal('0')

    # total price calculation when invalid
    for i, form in enumerate(registrant.forms):
        deleted = False
        if form.data.get('registrant-%d-DELETE' % count, False):
            deleted = True

        if is_table and i == 0:
            if i == 0:
                price_list.append({'price': individual_price_first , 'deleted':deleted})
                total_price += individual_price_first
        else:
            price_list.append({'price': individual_price , 'deleted':deleted})
            if not deleted:
                total_price += individual_price
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
        'free_event': event.free_event,
        'price_list':price_list,
        'total_price':total_price,
        'pricing': pricing,
        'reg_form':reg_form,
        'custom_reg_form': custom_reg_form,
        'registrant': registrant,
        'addons':addons,
        'addon_formset': addon_formset,
        'total_regt_forms': total_regt_forms,
        'has_registrant_form_errors': has_registrant_form_errors,
        'within_available_spots': within_available_spots
    }, context_instance=RequestContext(request))


@is_enabled('events')
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
    limit = event.get_limit()
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
                if request.user.profile.is_superuser and event_price > 0:
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
                            'payment.pay_online',
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

                    EventLog.objects.log(instance=event)

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


@is_enabled('events')
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
        entry_ids = reg8n.registrant_set.filter(cancel_dt__isnull=True
                                                ).values_list('custom_reg_form_entry',
                                                              flat=True).order_by('id')

        entries = CustomRegFormEntry.objects.filter(pk__in=entry_ids)

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
                                    fields=('first_name', 'last_name', 'company_name',
                                             'phone', 'email', 'comments'))
        formset = RegistrantFormSet(request.POST or None,
                                    queryset=Registrant.objects.filter(registration=reg8n,
                                                                       cancel_dt__isnull=True).order_by('id'))

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
                    entry = form.save(reg8n.event)
                    for reg in entry.registrants.all():
                        reg.initialize_fields()
                updated = True
            else:
                instances = formset.save()
                if instances: updated = True

            reg8n_conf_url = reverse(
                                    'event.registration_confirmation',
                                    args=(reg8n.event.id, reg8n.registrant.hash)
                                    )

            if updated:
                EventLog.objects.log(instance=reg8n)

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


@is_enabled('events')
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

                # Log an event for each registrant in the loop
                EventLog.objects.log(instance=registrant)

            registration.canceled = True
            registration.save()

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
            if not c_regt.name:
                c_regt.last_name = c_regt.name = c_regt.custom_reg_form_entry.__unicode__()

    return render_to_response(template_name, {
        'event': event,
        'registration': registration,
        'registrants': registrants,
        'cancelled_registrants': cancelled_registrants,
        'hash': hash,
        },
        context_instance=RequestContext(request))


@is_enabled('events')
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

            # check if all registrants in this registration are canceled.
            # if so, update the canceled field.
            reg8n = registrant.registration
            exist_not_canceled = Registrant.objects.filter(
                                registration=reg8n,
                                cancel_dt__isnull=True
                                ).exists()
            if not exist_not_canceled:
                reg8n.canceled = True
                reg8n.save()



            EventLog.objects.log(instance=registrant)

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


@is_enabled('events')
def month_view(request, year=None, month=None, type=None, template_name='events/month-view.html'):
    from datetime import date
    from tendenci.addons.events.utils import next_month, prev_month

    if type:  # redirect to /events/month/ if type does not exist
        if not Type.objects.filter(slug=type).exists():
            return HttpResponseRedirect(reverse('event.month'))

    # default/convert month and year
    if month and year:
        month, year = int(month), int(year)
    else:
        month, year = datetime.now().month, datetime.now().year

    if type and "latest" in request.GET:
        current_type = Type.objects.filter(slug=type)
        current_date = datetime(month=month, day=1, year=year)
        latest_event = Event.objects.filter(start_dt__gte=current_date, type=current_type[0]).order_by('start_dt')
        if latest_event.count() > 0:
            latest_month = latest_event[0].start_dt.month
            latest_year = latest_event[0].start_dt.year
            if not check_month(month, year, current_type[0]):
                current_date = current_date.strftime('%b %Y')
                latest_date = latest_event[0].start_dt.strftime('%b %Y')
                messages.add_message(request, messages.INFO, 'No %s Events were found for %s. The next %s event is on %s, shown below.' % (current_type[0], current_date, current_type[0], latest_date))
                return HttpResponseRedirect(reverse('event.month', args=[latest_year, latest_month, current_type[0].slug]))
        else:
            messages.add_message(request, messages.INFO, 'No more %s Events were found.' % (current_type[0]))

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

    EventLog.objects.log()

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


@is_enabled('events')
def day_view(request, year=None, month=None, day=None, template_name='events/day-view.html'):
    year = int(year)
    if year <= 1900:
        raise Http404

    day_date = datetime(year=int(year), month=int(month), day=int(day))
    yesterday = day_date - timedelta(days=1)
    yesterday_url = reverse('event.day', args=(
            int(yesterday.year),
            int(yesterday.month),
            int(yesterday.day)
        ))
    tomorrow = day_date + timedelta(days=1)
    tomorrow_url = reverse('event.day', args=(
            int(tomorrow.year),
            int(tomorrow.month),
            int(tomorrow.day)
        ))

    EventLog.objects.log()

    return render_to_response(template_name, {
        'date': day_date,
        'now': datetime.now(),
        'type': None,
        'yesterday': yesterday,
        'tomorrow': tomorrow,
        'yesterday_url': yesterday_url,
        'tomorrow_url': tomorrow_url,
    }, context_instance=RequestContext(request))


@is_enabled('events')
def today_redirect(request):
    today_date = request.GET.get('today_date', None)
    try:
        today_date = datetime.strptime(today_date, '%Y-%m-%d')
    except:
        today_date = datetime.now()

    day, month, year = today_date.day, today_date.month, today_date.year
    return HttpResponseRedirect(reverse('event.day', args=(int(year), int(month), int(day))))


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
                EventLog.objects.log(event_type="add", instance=event_type)

            # log "changed" event_types
            for event_type, changed_data in formset.changed_objects:
                EventLog.objects.log(event_type="edit", instance=event_type)

            # log "deleted" event_types
            for event_type in formset.deleted_objects:
                EventLog.objects.log(event_type="delete", instance=event_type)

    formset = TypeFormSet()

    return render_to_response(template_name, {'formset': formset},
        context_instance=RequestContext(request))


@login_required
def reassign_type(request, type_id, form_class=ReassignTypeForm, template_name='events/types/reassign.html'):
    type = get_object_or_404(Type, pk=type_id)

    form = form_class(request.POST or None, type_id=type.id)

    if request.method == 'POST':
        if form.is_valid():
            type.event_set.update(type=form.cleaned_data['type'])
            messages.add_message(request, messages.SUCCESS, 'Successfully reassigned events from type "%s" to type "%s".' % (type, form.cleaned_data['type']))
            return redirect('event.search')

    return render_to_response(template_name, {'type': type, 'form': form},
        context_instance=RequestContext(request))


@is_enabled('events')
def global_registrant_search(request, template_name='events/registrants/global-search.html'):

    form = RegistrantSearchForm(request.GET)

    if form.is_valid():
        event = form.cleaned_data.get('event')
        start_dt = form.cleaned_data.get('start_dt')
        end_dt = form.cleaned_data.get('end_dt')

        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        email = form.cleaned_data.get('email')
        user_id = form.cleaned_data.get('user_id')

    registrants = Registrant.objects.order_by("-update_dt")

    if event:
        registrants = registrants.filter(registration__event=event)
    if start_dt:
        registrants = registrants.filter(registration__event__start_dt__gte=start_dt)
    if end_dt:
        registrants = registrants.filter(registration__event__end_dt__lte=end_dt)
    try:
        registrants = registrants.filter(user=user_id)
    except ValueError:
        pass

    registrants = (registrants.filter(first_name__icontains=first_name)
                              .filter(last_name__icontains=last_name)
                              .filter(email__icontains=email))

    return render_to_response(template_name, {
        'registrants': registrants,
        'form': form,
        }, context_instance=RequestContext(request))


@is_enabled('events')
@login_required
def registrant_search(request, event_id=0, template_name='events/registrants/search.html'):
    query = request.GET.get('q', None)
    page = request.GET.get('page', 1)

    event = get_object_or_404(Event, pk=event_id)

    if not (has_perm(request.user,'events.view_registrant') or has_perm(request.user,'events.change_event', event)):
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
        active_registrants = Registrant.objects.filter(registration__event=event).filter(cancel_dt=None).order_by("-update_dt")
        canceled_registrants = Registrant.objects.filter(registration__event=event).exclude(cancel_dt=None).order_by("-update_dt")

    all_registrants = registrants

    if page:
        registrants_paginator = Paginator(registrants, 10)
        try:
            registrants = registrants_paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            registrants = registrants_paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            registrants = registrants_paginator.page(registrants_paginator.num_pages)

    for reg in registrants:
        if hasattr(reg, 'object'): reg = reg.object
        if reg.custom_reg_form_entry:
            reg.assign_mapped_fields()
            reg.non_mapped_field_entries = reg.custom_reg_form_entry.get_non_mapped_field_entry_list()
            if not reg.name:
                reg.name = reg.custom_reg_form_entry.__unicode__()

    EventLog.objects.log(instance=event)

    return render_to_response(template_name, {
        'event':event,
        'registrants':registrants,
        'all_registrants': all_registrants,
        'active_registrants':active_registrants,
        'canceled_registrants':canceled_registrants,
        'query': query,
        }, context_instance=RequestContext(request))


@is_enabled('events')
@login_required
def registrant_roster(request, event_id=0, roster_view='', template_name='events/registrants/roster.html'):
    # roster_view in ['total', 'paid', 'non-paid']
    from django.db.models import Sum
    event = get_object_or_404(Event, pk=event_id)
    has_addons = event.has_addons

    if not (has_perm(request.user, 'events.view_registrant') or has_perm(request.user, 'events.change_event', event)):
        raise Http403

    sort_order = request.GET.get('sort_order', 'last_name')
    sort_type = request.GET.get('sort_type', 'asc')

    if sort_order not in ('first_name', 'last_name', 'company_name'):
        sort_order = 'last_name'
    if sort_type not in ('asc', 'desc'):
        sort_type = 'asc'
    sort_field = sort_order
    if sort_type == 'desc':
        sort_field = '-%s' % sort_field

    if not roster_view:  # default to total page
        roster_view = 'total'

    # paid or non-paid or total
    registrations = Registration.objects.filter(event=event, canceled=False)

    if roster_view == 'paid':
        registrations = registrations.filter(invoice__balance__lte=0)
    elif roster_view == 'non-paid':
        registrations = registrations.filter(invoice__balance__gt=0)

    # Collect the info for custom reg form fields
    # and store the values in roster_fields_dict.
    # The key of roster_fields_dict is the entry.id.
    # The map of entry.id and registrant.id is in the
    # dictionary reg_form_entries_dict.
    # This is to reduce the # of database queries.
    roster_fields_dict = {}
    # [(110, 11), (111, 10),...]
    reg_form_entries = Registrant.objects.filter(
        registration__event=event,
        cancel_dt=None).values_list('id', 'custom_reg_form_entry')

    # a dictionary of registrant.id as key and entry as value
    reg_form_entries_dict = dict(reg_form_entries)

    if reg_form_entries:
        reg_form_field_entries = CustomRegFieldEntry.objects.filter(
            entry__in=[entry[1] for entry in reg_form_entries if entry[1] is not None],
            field__display_on_roster=1
        ).exclude(field__map_to_field__in=[
            'first_name',
            'last_name',
            'email',
            'phone',
            'position_title',
            'company_name',
            'comments'
        ]).select_related().values_list(
            'entry__id',
            'field__label',
            'value'
        ).order_by('field__position')

        if reg_form_field_entries:
            for field_entry in reg_form_field_entries:
                key = str(field_entry[0])
                if not key in roster_fields_dict:
                    roster_fields_dict[key] = []
                roster_fields_dict[key].append({'label': field_entry[1], 'value': field_entry[2]})

    registrants = Registrant.objects.filter(
        registration__event=event, cancel_dt=None)

    if roster_view in ('paid', 'non-paid'):
        registrants = registrants.filter(registration__in=registrations)

    # get the total checked in
    total_checked_in = registrants.filter(checked_in=True).count()

    # Pricing title - store with the registrant to improve the performance.
    pricing_titles = RegConfPricing.objects.filter(
        reg_conf=event.registration_configuration).values_list('id', 'title')
    pricing_titles_dict = dict(pricing_titles)

    # Store the price and invoice info with registrants to reduce the # of queries.
    # need 4 mappings:
    #    1) registrant_ids to pricing_ids
    #    2) registration_ids to pricings_ids
    #    3) registrant_ids to registration_ids
    #    4) registration_ids to invoices
    reg7n_pricing_reg8n = registrants.values_list('id', 'pricing__id', 'registration__id')
    reg7n_to_pricing_dict = dict([(item[0], item[1]) for item in reg7n_pricing_reg8n])
    reg8n_to_pricing_dict = dict(registrations.values_list('id', 'reg_conf_price__id'))
    reg7n_to_reg8n_dict = dict([(item[0], item[2]) for item in reg7n_pricing_reg8n])
    reg8n_to_invoice_objs = registrations.values_list(
        'id',
        'invoice__id',
        'invoice__total',
        'invoice__balance',
        'invoice__admin_notes',
        'invoice__tender_date')

    reg8n_to_invoice_dict = {}
    invoice_fields = ('id', 'total', 'balance', 'admin_notes', 'tender_date')
    for item in reg8n_to_invoice_objs:
        if item[1] == None:
            reg8n_to_invoice_dict[item[0]] = dict(zip(invoice_fields, (0, 0, 0, '', '')))
        else:
            reg8n_to_invoice_dict[item[0]] = dict(zip(invoice_fields, item[1:]))

    # registration to list of registrants mapping
    reg8n_to_reg7n_dict = {}
    for k, v in reg7n_to_reg8n_dict.iteritems():
        reg8n_to_reg7n_dict.setdefault(v, []).append(k)

    if sort_field in ('first_name', 'last_name'):
        # let registrants without names sink dowm to the bottom
        regisrants_noname = registrants.filter(
            last_name='', first_name='').select_related('user').order_by('id')

        registrants_withname = registrants.exclude(
            last_name='', first_name='').select_related('user').order_by(sort_field)

        c = itertools.chain(registrants_withname, regisrants_noname)
        registrants = [r for r in c]
    else:
        registrants = registrants.order_by(sort_field).select_related('user')

    if roster_fields_dict:
        for registrant in registrants:
            # assign custom form roster_field_list (if any) to registrants
            key = str(reg_form_entries_dict[registrant.id])
            if key in roster_fields_dict:
                registrant.roster_field_list = roster_fields_dict[key]

    num_registrants_who_paid = 0
    num_registrants_who_owe = 0

    for registrant in registrants:
        # assign pricing title to the registrants
        key = reg7n_to_pricing_dict[registrant.id]
        if not key in pricing_titles_dict:
            if reg7n_to_reg8n_dict[registrant.id] in reg8n_to_pricing_dict:
                key = reg8n_to_pricing_dict[reg7n_to_reg8n_dict[registrant.id]]
        if key in pricing_titles_dict:
            registrant.price_title = pricing_titles_dict[key]
        else:
            registrant.price_title = 'Untitled'

        # assign invoice dict
        key = reg7n_to_reg8n_dict[registrant.id]
        if key in reg8n_to_invoice_dict:
            registrant.invoice_dict = reg8n_to_invoice_dict[key]
            if registrant.invoice_dict['balance'] <= 0:
                num_registrants_who_paid += 1
            else:
                num_registrants_who_owe += 1

    for registrant in registrants:
        # assign additional registrants
        registrant.additionals = []
        key = reg7n_to_reg8n_dict[registrant.id]
        if reg8n_to_reg7n_dict[key]:
            additional_ids = [id for id in reg8n_to_reg7n_dict[key]]
            additional_ids.remove(registrant.id)
            if additional_ids:
                for r in registrants:
                    if r.id in additional_ids:
                        registrant.additionals.append(r)

    # assign addons
    addon_total_sum = Decimal('0')
    if has_addons:
        reg8n_to_addons_list = RegAddonOption.objects.filter(
            regaddon__registration__in=registrations).values_list(
                'regaddon__registration__id',
                'regaddon__addon__title',
                'option__title',
                'regaddon__amount')

        if reg8n_to_addons_list:
            addon_total_sum = sum([item[3] for item in reg8n_to_addons_list])
            for registrant in registrants:
                if registrant.is_primary:
                    registrant.addons = ''
                    registrant.addons_amount = Decimal('0')
                    for addon_item in reg8n_to_addons_list:
                        if addon_item[0] == registrant.registration_id:
                            registrant.addons += '%s(%s) ' % (addon_item[1], addon_item[2])
                            registrant.addons_amount += addon_item[3]

    total_sum = float(0)
    balance_sum = float(0)

    # Get the total_sum and balance_sum.
    totals_d = registrations.aggregate(
        total_sum=Sum('invoice__total'), balance_sum=Sum('invoice__balance'))
    total_sum = totals_d['total_sum']
    balance_sum = totals_d['balance_sum']

    EventLog.objects.log(instance=event)

    return render_to_response(template_name, {
        'event': event,
        'registrants': registrants,
        'balance_sum': balance_sum,
        'total_sum': total_sum,
        'num_registrants_who_paid': num_registrants_who_paid,
        'num_registrants_who_owe': num_registrants_who_owe,
        'roster_view': roster_view,
        'sort_order': sort_order,
        'sort_type': sort_type,
        'has_addons': has_addons,
        'addon_total_sum': addon_total_sum,
        'total_checked_in': total_checked_in}, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def registrant_check_in(request):
    """
    Check in or uncheck in a registrant.
    """
    response_d = {'error': True}
    if request.method == 'POST':
        registrant_id = request.POST.get('id', None)
        action = request.POST.get('action', None)
        if registrant_id and action:
            [registrant] = Registrant.objects.filter(id=registrant_id)[:1] or [None]
            if registrant:
                if action == 'checked_in':
                    if not registrant.checked_in:
                        registrant.checked_in = True
                        registrant.checked_in_dt = datetime.now()
                        registrant.save()
                    response_d['checked_in_dt'] = registrant.checked_in_dt
                    if isinstance(response_d['checked_in_dt'], datetime):
                        response_d['checked_in_dt'] = response_d['checked_in_dt'].strftime('%m/%d %I:%M%p')
                elif action == 'not_checked_in':
                    if registrant.checked_in:
                        registrant.checked_in = False
                        registrant.save()
                    response_d['checked_in_dt'] = ''
                response_d['error'] = False

    return HttpResponse(json.dumps(response_d), mimetype="text/plain")


@is_enabled('events')
@login_required
def registrant_details(request, id=0, hash='', template_name='events/registrants/details.html'):
    registrant = get_object_or_404(Registrant, pk=id)

    if has_perm(request.user,'registrants.view_registrant',registrant):
        EventLog.objects.log(instance=registrant)

        return render_to_response(template_name, {'registrant': registrant},
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('events')
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
            if registrant.first_name or registrant.last_name:
                registrant.name = ' '.join([registrant.first_name, registrant.last_name])
    EventLog.objects.log(instance=registration)

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
    from tendenci.core.emails.models import Email
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

            EventLog.objects.log(instance=email)

            messages.add_message(request, messages.SUCCESS, 'Successfully sent email "%s" to event registrants for event "%s".' % (subject, event.title))

            return HttpResponseRedirect(reverse('event', args=([event_id])))

    else:
        defaultsubject = render_to_string('events/message/subject-text.txt', {'event': event},
            context_instance=RequestContext(request))
        openingtext = render_to_string('events/message/opening-text.txt', {'event': event},
            context_instance=RequestContext(request))
        form = form_class(event.id, initial={'subject':defaultsubject, 'body': openingtext})

    return render_to_response(template_name, {
        'event':event,
        'form': form
        },context_instance=RequestContext(request))


@login_required
def edit_email(request, event_id, form_class=EmailForm, template_name='events/edit_email.html'):
    event = get_object_or_404(Event, pk=event_id)
    if not has_perm(request.user,'events.change_event',event): raise Http403

    reg_conf = event.registration_configuration
    email = reg_conf.email

    if request.method == "POST":
        form = form_class(request.POST, instance=email)
        if form.is_valid():
            email = form.save(commit=False)
            if not email.id:
                email.creator = request.user
                email.creator_username = request.user.username

            email.owner = request.user
            email.owner_username = request.user.username
            email.save()

            if not reg_conf.email:
                reg_conf.email = email
                reg_conf.save()

            messages.add_message(request, messages.SUCCESS, 'Successfully saved changes.')

            if request.POST.get('submit', '') == 'Save & Test':
                render_event_email(event, email)
                site_url = get_setting('site', 'global', 'siteurl')
                email.recipient = request.user.email
                email.subject = "Reminder: %s" % email.subject
                email.body = convert_absolute_urls(email.body, site_url)
                email.send()

                messages.add_message(request, messages.SUCCESS, 'Successfully sent a test email.')

    else:
        if not email:
            openingtext = get_default_reminder_template(event)
            [organizer] = Organizer.objects.filter(event=event)[:1] or [None]
            form = form_class(initial={
                                     'subject': '{{ event_title }}',
                                     'body': openingtext,
                                     'reply_to': organizer and organizer.user \
                                      and organizer.user.email or request.user.email,
                                     'sender_display': organizer and organizer.name})
        else:
            form = form_class(instance=email)

    return render_to_response(template_name, {
        'event':event,
        'form': form
        },context_instance=RequestContext(request))


@is_enabled('events')
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
        ('position_title', 'position_title'),
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

    EventLog.objects.log(instance=event)

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s' % file_name
    book.save(response)
    return response


@is_enabled('events')
def registrant_export_with_custom(request, event_id, roster_view=''):
    """
    Export all registration for a specific event with or without custom registration forms
    """
    event = get_object_or_404(Event, pk=event_id)

    # if they can edit it, they can export it
    if not has_perm(request.user, 'events.change_event', event):
        raise Http403

    import xlwt
    from ordereddict import OrderedDict

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
        file_name = event.title.strip().replace(' ', '-')
        file_name = 'Event-%s-Non-Paid.xls' % re.sub(r'[^a-zA-Z0-9._]+', '', file_name)
    elif roster_view == 'paid':
        registrants = event.registrants(with_balance=False)
        file_name = event.title.strip().replace(' ', '-')
        file_name = 'Event-%s-Paid.xls' % re.sub(r'[^a-zA-Z0-9._]+', '', file_name)
    else:
        registrants = event.registrants()
        file_name = event.title.strip().replace(' ', '-')
        file_name = 'Event-%s-Total.xls' % re.sub(r'[^a-zA-Z0-9._]+', '', file_name)

    from collections import namedtuple

    # the key is what the column will be in the
    # excel sheet. the value is the database lookup
    # Used OrderedDict to maintain the column order
    registrant_mappings = OrderedDict([
        ('first_name', 'first_name'),
        ('last_name', 'last_name'),
        ('phone', 'phone'),
        ('email', 'email'),
        ('position_title', 'position_title'),
        ('company', 'company_name'),
        ('address', 'address'),
        ('city', 'city'),
        ('state', 'state'),
        ('zip', 'zip'),
        ('country', 'country'),
        ('date', 'create_dt'),
        ('registration_id', 'registration__pk'),
        ('is_primary', 'is_primary'),
        ('amount', 'amount'),
        ('price type', 'registration__reg_conf_price__title'),
        ('invoice_id', 'registration__invoice__pk'),
        ('registration price', 'registration__invoice__total'),
        ('payment method', 'registration__payment_method__machine_name'),
        ('balance', 'registration__invoice__balance'),
    ])

    RegistrantTuple = namedtuple('Registrant', registrant_mappings.values())

    registrant_lookups = registrant_mappings.values()

    # Append the heading to the list of values that will
    # go into the excel sheet
    values_list = []

    # registrants with regular reg form
    non_custom_registrants = registrants.filter(custom_reg_form_entry=None)
    non_custom_registrants = non_custom_registrants.values('pk', *registrant_lookups)

    if non_custom_registrants:
        values_list.insert(0, registrant_mappings.keys() + ['is_paid', 'primary_registrant'])

        for registrant_dict in non_custom_registrants:

            is_paid = False
            primary_registrant = u'-- N/A ---'

            # update registrant values
            if not registrant_dict['is_primary']:

                is_paid = (registrant_dict['registration__invoice__balance'] == 0)
                primary_registrant = Registrant.objects.get(pk=registrant_dict['pk'])

                registrant = Registrant.objects.get(pk=registrant_dict['pk'])
                primary_registrant = registrant.registration.registrant

                if primary_registrant:
                    primary_registrant = '%s %s' % (primary_registrant.first_name, primary_registrant.last_name)

                registrant_dict['registration__invoice__total'] = 0
                registrant_dict['registration__invoice__balance'] = 0

            del registrant_dict['pk']

            # keeps order of values
            registrant_tuple = RegistrantTuple(**registrant_dict)

            values_list.append(tuple(registrant_tuple) + (is_paid, primary_registrant))

        values_list.append(['\n'])

    # Write the data enumerated to the excel sheet
    balance_index = 17
    start_row = 0
    render_registrant_excel(sheet, values_list, balance_index, styles, start=start_row)
    start_row += len(values_list)

    # ***now check for the custom registration forms***
    custom_reg_exists = Registrant.objects.filter(
        registration__event=event).exclude(custom_reg_form_entry=None).exists()

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
            fields = CustomRegField.objects.filter(
                form=custom_reg_form).order_by('position').values_list('id', 'label')

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

            balance_index = len(field_ids) + len(registrant_lookups) - 1

            # write to spread sheet
            render_registrant_excel(sheet, rows_list, balance_index, styles, start=start_row)
            start_row += len(rows_list)

    EventLog.objects.log(instance=event)

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s' % file_name
    book.save(response)
    return response


@is_enabled('events')
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


@is_enabled('events')
@login_required
def delete_group_pricing(request, id):
    if not has_perm(request.user,'events.delete_registrationconfiguration'):
        raise Http403

    gp = get_object_or_404(GroupRegistrationConfiguration, id = id)
    event = Event.objects.get(registration_configuration=gp.config)

    messages.add_message(request, messages.SUCCESS, 'Successfully deleted Group Pricing for %s' % gp)

    gp.delete()

    return redirect('event', id=event.id)


@is_enabled('events')
@login_required
def delete_special_pricing(request, id):
    if not has_perm(request.user,'events.delete_registrationconfiguration'):
        raise Http403

    s = get_object_or_404(SpecialPricing, id = id)
    event = Event.objects.get(registration_configuration=s.config)

    messages.add_message(request, messages.SUCCESS, 'Successfully deleted Special Pricing for %s' % s)

    s.delete()

    return redirect('event', id=event.id)


@is_enabled('events')
@login_required
def copy(request, id):
    if not has_perm(request.user, 'events.add_event'):
        raise Http403

    event = get_object_or_404(Event, id=id)
    new_event = copy_event(event, request.user)

    EventLog.objects.log(instance=new_event)

    messages.add_message(request, messages.SUCCESS, 'Sucessfully copied Event: %s.<br />Edit the new event (set to <strong>private</strong>) below.' % new_event.title)

    return redirect('event.edit', id=new_event.id)


@is_enabled('events')
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
            event.save(log=False)

            # save photo
            photo = form.cleaned_data['photo_upload']
            if photo: event.save(photo=photo)

            messages.add_message(request, messages.SUCCESS,
                'Your event submission has been received. It is now subject to approval.')
            return redirect('events')
    else:
        form = form_class(user=request.user, prefix="event")
        form_place = PlaceForm(prefix="place")

    return render_to_response(template_name, {
        'form': form,
        'form_place': form_place,
        }, context_instance=RequestContext(request))


@is_enabled('events')
@login_required
def pending(request, template_name="events/pending.html"):
    """
    Show a list of pending events to be approved.
    """
    if not request.user.profile.is_superuser:
        raise Http403

    events = Event.objects.filter(status=False, status_detail='pending').order_by('start_dt')

    EventLog.objects.log()

    return render_to_response(template_name, {
        'events': events,
        }, context_instance=RequestContext(request))


@login_required
def approve(request, event_id, template_name="events/approve.html"):
    """
    Approve a selected event
    """

    if not request.user.profile.is_superuser:
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

            EventLog.objects.log(instance=addon)

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

            EventLog.objects.log(instance=addon)

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
    """disable addon for an event"""
    event = get_object_or_404(Event, pk=event_id)

    if not has_perm(request.user,'events.change_event', event):
        raise Http404

    addon = get_object_or_404(Addon, pk=addon_id)
    EventLog.objects.log(instance=addon)
    addon.delete() # this just renders it inactive to not cause deletion of already existing regaddons
    messages.add_message(request, messages.SUCCESS, "Successfully disabled the %s" % addon.title)

    return redirect('event.list_addons', event.id)


@login_required
def enable_addon(request, event_id, addon_id):
    """enable addon for an event"""
    event = get_object_or_404(Event, pk=event_id)

    if not has_perm(request.user,'events.change_event', event):
        raise Http404

    addon = get_object_or_404(Addon, pk=addon_id)
    addon.status = True
    addon.save()

    EventLog.objects.log(instance=addon)

    messages.add_message(request, messages.SUCCESS,
        "Successfully enabled the %s" % addon.title)

    return redirect('event.list_addons', event.id)


@is_enabled('events')
@login_required
def export(request, template_name="events/export.html"):
    """Export Events"""
    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        export_id = run_export_task('events', 'event', [])
        return redirect('export.status', export_id)

    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))


@login_required
def create_ics(request, template_name="events/ics.html"):
    """Create ICS"""

    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        form = EventICSForm(request.POST)
        if form.is_valid():
            ics_id = run_precreate_ics('events', 'event', form.cleaned_data['user'])
            return redirect('ics.status', ics_id)
    else:
        form = EventICSForm()

    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))


@is_enabled('events')
@login_required
def myevents(request, template_name='events/myevents.html'):
    """ Logged-in user's registered events"""
    if 'all' not in request.GET:
        events = Event.objects.filter(registration__registrant__email=request.user.email).exclude(end_dt__lt=datetime.now())
        show = 'True'
    else:
        events = Event.objects.filter(registration__registrant__email=request.user.email)
        show = None

    events = events.order_by('-start_dt')

    types = Type.objects.all().order_by('name')

    EventLog.objects.log()

    return render_to_response(
        template_name,
        {'events': events, 'show': show},
        context_instance=RequestContext(request))


@login_required
def download_template_csv(request, file_ext='.csv'):
    if not request.user.profile.is_superuser:
        raise Http403

    if file_ext == '.csv':
        filename = "import-events.csv"
    else:
        filename = "import-events.xls"
    import_field_list = [
        "type",
        "title",
        "description",
        "all_day",
        "start_dt",
        "end_dt",
        "timezone",
        "place__name",
        "place__description",
        "place__address",
        "place__city",
        "place__state",
        "place__zip",
        "place__country",
        "place__url",
        "on_weekend",
        "external_url",
    ]
    data_row_list = []

    return render_excel(filename, import_field_list, data_row_list, file_ext)


@login_required
def import_add(request, form_class=ImportForm,
                    template_name="events/imports/events_add.html"):
    """Event Import Step 1: Validates and saves import file"""
    if not request.user.profile.is_superuser:
        raise Http403

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            import_i = form.save(commit=False)
            import_i.app_label = 'events'
            import_i.model_name = 'event'
            import_i.save()

            EventLog.objects.log()

            # reset the password_promt session
            del request.session['password_promt']

            return HttpResponseRedirect(
                reverse('event.import_preview', args=[import_i.id]))
    else:
        form = form_class()
    return render_to_response(template_name, {'form': form},
        context_instance=RequestContext(request))


@login_required
def import_preview(request, import_id,
                    template_name="events/imports/events_preview.html"):
    """Import Step 2: Preview import result"""

    if not request.user.profile.is_superuser:
        raise Http403

    import_i = get_object_or_404(Import, id=import_id)

    event_list, invalid_list = event_import_process(import_i,
                                                        preview=True)

    return render_to_response(template_name, {
        'total': import_i.total_created + import_i.total_invalid,
        'event_list': event_list,
        'import_i': import_i,
    }, context_instance=RequestContext(request))


@login_required
def import_process(request, import_id,
                template_name="events/imports/events_process.html"):
    """Import Step 3: Import into database"""

    if not request.user.profile.is_superuser:
        raise Http403   # admin only page

    import_i = get_object_or_404(Import, id=import_id)

    subprocess.Popen(['python', 'manage.py', 'import_events', str(import_id)])

    return render_to_response(template_name, {
        'total': import_i.total_created + import_i.total_invalid,
        "import_i": import_i,
    }, context_instance=RequestContext(request))
