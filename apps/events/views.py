import calendar
from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages

from base.http import Http403
from site_settings.utils import get_setting
from events.models import Event, RegistrationConfiguration, Registration, Registrant, Speaker, Organizer, Type, PaymentMethod
from events.forms import EventForm, Reg8nForm, Reg8nEditForm, PlaceForm, SpeakerForm, OrganizerForm, TypeForm
from events.search_indexes import EventIndex
from events.utils import save_registration
from perms.models import ObjectPermission
from perms.utils import get_administrators
from perms.utils import has_perm
from event_logs.models import EventLog
from invoices.models import Invoice
from meta.models import Meta as MetaTags
from meta.forms import MetaForm


try: from notification import models as notification
except: notification = None

def index(request, id=None, template_name="events/view.html"):

    if not id:
        return HttpResponseRedirect(reverse('event.month'))

    event = get_object_or_404(Event, pk=id)
    
    if has_perm(request.user,'events.view_event',event):

        EventLog.objects.log(
            event_id =  175000, # view event
            event_data = '%s (%d) viewed by %s' % (event._meta.object_name, event.pk, request.user),
            description = '%s viewed' % event._meta.object_name,
            user = request.user,
            request = request,
            instance = event
        )

        
        try: speaker = event.speaker_set.all()[0]
        except: speaker = None

        try: organizer = event.organizer_set.all()[0]
        except: organizer = None

        return render_to_response(template_name, {
            'event': event,
            'speaker': speaker,
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
        event_id =  174000, # searched event
        event_data = '%s searched by %s' % ('Event', request.user),
        description = 'Event searched',
        user = request.user,
        request = request,
        source = 'events',
    )

    return render_to_response(template_name, {'events':events, 'now':datetime.now()}, 
        context_instance=RequestContext(request))
    
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
        event_id =  175001, # print view event
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
    
@login_required
def edit(request, id, form_class=EventForm, template_name="events/edit.html"):
    event = get_object_or_404(Event, pk=id)

    # tried get_or_create(); but get a keyword argument :(
    try: # look for a speaker
        speaker = event.speaker_set.all()[0]
    except: # else: create a speaker
        speaker = Speaker()
        speaker.save()
        speaker.event = [event]
        speaker.save()

    # tried get_or_create(); but get a keyword argument :(
    try: # look for a speaker
        organizer = event.organizer_set.all()[0]
    except: # else: create a speaker
        organizer = Organizer()
        organizer.save()
        organizer.event = [event]
        organizer.save()

    if has_perm(request.user,'events.change_event',event):    
        if request.method == "POST":

            form_event = form_class(request.POST, instance=event, user=request.user)
            if form_event.is_valid():
                event = form_event.save(commit=False)
                event.creator_username = request.user.username
                event.owner_username = request.user.username
                event.owner = request.user

                # set up user permission
                event.allow_user_view, event.allow_user_edit = form_event.cleaned_data['user_perms']
                
                # assign permissions
                ObjectPermission.objects.remove_all(event)
                ObjectPermission.objects.assign_group(form_event.cleaned_data['group_perms'], event)
                ObjectPermission.objects.assign(event.creator, event) 
                
                event.save()

                EventLog.objects.log(
                    event_id =  172000, # edit event
                    event_data = '%s (%d) edited by %s' % (event._meta.object_name, event.pk, request.user),
                    description = '%s edited' % event._meta.object_name,
                    user = request.user,
                    request = request,
                    instance = event,
                )

                # location validation
                form_place = PlaceForm(request.POST, instance=event.place, prefix='place')
                if form_place.is_valid():
                    place = form_place.save() # save place
                    event.place = place
                    event.save() # save event

                # speaker validation
                form_speaker = SpeakerForm(request.POST, instance=speaker, prefix='speaker')
                if form_speaker.is_valid():
                    speaker = form_speaker.save(commit=False)                   
                    speaker.event = [event]
                    speaker.save()

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

                forms = [
                    form_event,
                    form_place,
                    form_speaker,
                    form_organizer,
                    form_regconf,
                ]

                if all([form.is_valid() for form in forms]):
                    messages.add_message(request, messages.INFO, 'Successfully updated %s' % event)
                    if notification: notification.send(get_administrators(),'event_edited', {'object': event, 'request': request})
                    return HttpResponseRedirect(reverse('event', args=[event.pk]))
        else:

            form_event = form_class(instance=event, user=request.user)
            form_place = PlaceForm(instance=event.place, prefix='place')
            form_speaker = SpeakerForm(instance=speaker, prefix='speaker')
            form_organizer = OrganizerForm(instance=organizer, prefix='organizer')
            form_regconf = Reg8nEditForm(instance=event.registration_configuration, prefix='regconf')

        # response
        return render_to_response(template_name, {
            'event': event,
            'multi_event_forms':[form_event,form_place,form_speaker,form_organizer,form_regconf],
            'form_event':form_event,
            'form_place':form_place,
            'form_speaker':form_speaker,
            'form_organizer':form_organizer,
            'form_regconf':form_regconf,
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

    if has_perm(request.user,'events.add_event'):
        if request.method == "POST":

            form_event = form_class(request.POST, user=request.user)
            if form_event.is_valid():           
                event = form_event.save(commit=False)
                event.creator = request.user
                event.creator_username = request.user.username
                event.owner = request.user
                event.owner_username = request.user.username

                # tried get_or_create();
                try: # look for a speaker
                    speaker = event.speaker_set.all()[0]
                except: # else: create a speaker
                    speaker = Speaker()

                try: # look for an organizer
                    organizer = event.organizer_set.all()[0]
                except: # else: create an organizer
                    organizer = Organizer()

                form_place = PlaceForm(request.POST, 
                    instance=event.place, prefix='place')
                form_speaker = SpeakerForm(request.POST, 
                    instance=speaker, prefix='speaker')
                form_organizer = OrganizerForm(request.POST, 
                    instance=organizer, prefix='organizer')
                form_regconf = Reg8nEditForm(request.POST, 
                    instance=event.registration_configuration, prefix='regconf')

                forms = [
                    form_event,
                    form_place,
                    form_speaker,
                    form_organizer,
                    form_regconf,
                ]

                if all([form.is_valid() for form in forms]):

                    # pks have to exist; before making relationships
                    place = form_place.save()
                    regconf = form_regconf.save()
                    speaker = form_speaker.save()
                    organizer = form_organizer.save()
                    event.save()

                    # update supplemental
                    speaker.event = [event]
                    organizer.event = [event]

                    speaker.save() # save again
                    organizer.save() # save again

                    # update event
                    event.place = place
                    event.registration_configuration = regconf
                    
                    event.save() # save again

                    # event security
                    event.allow_user_view, event.allow_user_edit = form_event.cleaned_data['user_perms']
                    ObjectPermission.objects.assign_group(form_event.cleaned_data['group_perms'], event)
                    ObjectPermission.objects.assign(event.creator, event) 

                    EventLog.objects.log(
                        event_id =  171000, # add event
                        event_data = '%s (%d) added by %s' % (event._meta.object_name, event.pk, request.user),
                        description = '%s added' % event._meta.object_name,
                        user = request.user,
                        request = request,
                        instance = event
                    )

                    messages.add_message(request, messages.INFO, 'Successfully added %s' % event)
                    if notification: notification.send(get_administrators(),'event_added', {'object': event, 'request': request})
                    return HttpResponseRedirect(reverse('event', args=[event.pk]))

                return render_to_response(template_name, {
                    'multi_event_forms':[form_event,form_place,form_speaker,form_organizer,form_regconf],
                    'form_event':form_event,
                    'form_place':form_place,
                    'form_speaker':form_speaker,
                    'form_organizer':form_organizer,
                    'form_regconf':form_regconf,
                    }, 
                    context_instance=RequestContext(request))
        else:
            reg_inits = {
                'early_dt': datetime.now(),
                'regular_dt': datetime.now(),
                'late_dt': datetime.now(),
             }

            form_event = form_class(user=request.user)
            form_place = PlaceForm(prefix='place')
            form_speaker = SpeakerForm(prefix='speaker')
            form_organizer = OrganizerForm(prefix='organizer')
            form_regconf = Reg8nEditForm(initial=reg_inits, prefix='regconf')

            # response
            return render_to_response(template_name, {
                'multi_event_forms':[form_event,form_place,form_speaker,form_organizer,form_regconf],
                'form_event':form_event,
                'form_place':form_place,
                'form_speaker':form_speaker,
                'form_organizer':form_organizer,
                'form_regconf':form_regconf,
                }, 
                context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def delete(request, id, template_name="events/delete.html"):
    event = get_object_or_404(Event, pk=id)

    if has_perm(request.user,'events.delete_event'):   
        if request.method == "POST":

            EventLog.objects.log(
                event_id =  173000, # delete event
                event_data = '%s (%d) deleted by %s' % (event._meta.object_name, event.pk, request.user),
                description = '%s deleted' % event._meta.object_name,
                user = request.user,
                request = request,
                instance = event
            )

            messages.add_message(request, messages.INFO, 'Successfully deleted %s' % event)
            if notification: notification.send(get_administrators(),'event_deleted', {'object': event, 'request': request})

            event.delete()

            return HttpResponseRedirect(reverse('event.search'))
    
        return render_to_response(template_name, {'event': event}, 
            context_instance=RequestContext(request))
    else:
        raise Http403# Create your views here.

def register(request, event_id=0, form_class=Reg8nForm, template_name="events/reg8n/register.html"):
        event = get_object_or_404(Event, pk=event_id)

        user_account = None
        if isinstance(request.user, User):
            user_account = request.user
            user_email = user_account.email

        # free or priced event (choose template)
        free = (event.registration_configuration.price == 0)                
        if free: template_name = "events/reg8n/register-free.html"
        else: template_name = "events/reg8n/register-priced.html"

        # check for registry; else 404
        if not RegistrationConfiguration.objects.filter(event=event).exists():
            raise Http404

        try: # if they're registered (already); show them their confirmation
            reg8n = Registration.objects.get(event=event, registrant__user=request.user)
            return HttpResponseRedirect(reverse('event.registration_confirmation', args=(event_id, reg8n.pk)))
        except: pass

        # if the event has passed or registration deadline has passed;
        # redirect to detail page; this page explains the closed event
        if event.end_dt < datetime.now() or event.registration_configuration.late_dt < datetime.now():
            return HttpResponseRedirect(reverse('event', args=(event_id)))

        if request.method == "POST":
            form = form_class(event_id, request.POST)
            if form.is_valid():

                price = form.cleaned_data['price']

                # anonymous registrant
                if not request.user.is_authenticated():

                    # get user fields
                    username = form.cleaned_data.get("username", None)
                    user_name = form.cleaned_data.get("name", None)
                    user_email = form.cleaned_data.get("email", None)
                    password = form.cleaned_data.get("password1", None)

#                    try: # if authenticate; then login
#                        user_account = authenticate(username=username, password=password)
#                        login(request, user_account)
#                    except:
#                        # else create user account and user profile
#                        from profiles.models import Profile
#                        user_account = User.objects.create_user(username, user_email, password)
#                        Profile.objects.create_profile(user_account)
#
#                        # then authenticate; then login
#                        user_account = authenticate(username=user_account.username, password=password)
#                        login(request, user_account)

                # create registration record; then take payment
                # this allows someone to be registered with an outstanding balance 
                reg8n, created = save_registration(
                    user = user_account,
                    name = user_name, 
                    email = user_email, 
                    event = event, 
                    payment_method=form.cleaned_data['payment_method'], 
                    price=price
                )

                site_label = get_setting('site', 'global', 'sitedisplayname')
                site_url = get_setting('site', 'global', 'siteurl')

                if created:
                    if notification:
                        notification.send_now(
                            [request.user], 
                            'event_registration_confirmation', 
                            {   'site_label': site_label,
                                'site_url': site_url,
                                'event': event,
                                'price': price,
                             },
                            True, # notice object created in DB
                            send=True, # assume yes; for confirmation send
                        )

                if (reg8n.payment_method.label).lower() == 'credit card' and created:

                    invoice = Invoice.objects.get(
                        invoice_object_type = 'event_registration', # TODO: remove hard-coded object_type (content_type)
                        invoice_object_type_id = reg8n.pk,
                    )

                    response = HttpResponseRedirect(reverse('payments.views.pay_online', args=[invoice.id, invoice.guid]))
                else:
                    response = HttpResponseRedirect(reverse('event.registration_confirmation', args=(event_id, reg8n.pk)))


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

                if free:
                # if free event; then register w/o payment method
                    reg8n, created = save_registration(
                        user=user_account,
                        email=user_email, 
                        event=event, 
                        payment_method=payment_method, 
                        price='0.00'
                    )
                    response = HttpResponseRedirect(reverse('event.registration_confirmation', args=(event_id, reg8n.pk)))
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

def month_view(request, year=None, month=None, type=None, template_name='events/month-view.html'):
    from datetime import date
    from events.utils import next_month, prev_month

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

    formset = TypeFormSet()

    # TODO: Find more optimal way of keeping
    # the events object properly indexed
    # Maybe index by something that doesn't change
    # such as the primary-key
    events = Event.objects.all()
    for event in events:
        EventIndex(Event).update_object(event)

    return render_to_response(template_name, {'formset': formset}, 
        context_instance=RequestContext(request))

@login_required
def registrant_search(request, event_id=0, template_name='events/registrants/search.html'):
    query = request.GET.get('q', None)

    event = get_object_or_404(Event, pk=event_id)
    registrants = Registrant.objects.search(query, user=request.user, event=event)

    return render_to_response(template_name, {'event':event, 'registrants':registrants}, 
        context_instance=RequestContext(request))

@login_required
def registrant_roster(request, event_id=0, template_name='events/registrants/roster.html'):
    from django.db.models import Sum

    query = request.GET.get('q', None)

    event = get_object_or_404(Event, pk=event_id)
    registrants = Registrant.objects.search(query, user=request.user, event=event)

    total_balance = Registration.objects.filter(event=event).aggregate(Sum('amount_paid'))['amount_paid__sum']
    

    return render_to_response(template_name, {
        'event':event, 'registrants':registrants, 'total_balance':total_balance}, 
        context_instance=RequestContext(request))

@login_required
def registrant_details(request, id=0, template_name='events/registrants/details.html'):
    registrant = get_object_or_404(Registrant, pk=id)
    
    if has_perm(request.user,'registrans.view_registrant',registrant):
        return render_to_response(template_name, {'registrant': registrant}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def registration_confirmation(request, id=0, registration_id=0, template_name='events/reg8n/register-confirm.html'):
    event = get_object_or_404(Event, pk=id)
    registration = get_object_or_404(Registration, pk=registration_id)

    try: registrant = registration.registrant_set.all()[0]
    except: raise Http404

    return render_to_response(template_name, {
        'event':event,
        'registration':registration,
        'registrant':registrant,
        }, 
        context_instance=RequestContext(request))



