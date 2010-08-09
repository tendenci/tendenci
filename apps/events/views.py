import calendar
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib import messages

from base.http import Http403
from events.models import Event, RegistrationConfiguration, Registration, Registrant
from events.forms import EventForm, Reg8nForm, Reg8nEditForm
from perms.models import ObjectPermission
from perms.utils import get_administrators
from event_logs.models import EventLog
from meta.models import Meta as MetaTags
from meta.forms import MetaForm

try:
    from notification import models as notification
except:
    notification = None

def index(request, id=None, template_name="events/view.html"):
    event = get_object_or_404(Event, pk=id)
    
    if request.user.has_perm('events.view_event', event):
        log_defaults = {
            'event_id' : 435000,
            'event_data': '%s (%d) viewed by %s' % (event._meta.object_name, event.pk, request.user),
            'description': '%s viewed' % event._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': event,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'event': event}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="events/search.html"):
    query = request.GET.get('q', None)
    events = Event.objects.search(query, user=request.user)

    log_defaults = {
        'event_id' : 434000,
        'event_data': '%s searched by %s' % ('Event', request.user),
        'description': '%s searched' % 'Event',
        'user': request.user,
        'request': request,
        'source': 'events'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'events':events}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="events/print-view.html"):
    event = get_object_or_404(Event, pk=id)    

    log_defaults = {
        'event_id' : 435000,
        'event_data': '%s (%d) viewed by %s' % (event._meta.object_name, event.pk, request.user),
        'description': '%s viewed' % event._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': event,
    }
    EventLog.objects.log(**log_defaults)
       
    if request.user.has_perm('events.view_event', event):
        return render_to_response(template_name, {'event': event}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def edit(request, id, form_class=EventForm, template_name="events/edit.html"):
    event = get_object_or_404(Event, pk=id)

    if request.user.has_perm('events.change_event', event):    
        if request.method == "POST":
            form = form_class(request.POST, instance=event, user=request.user)
            if form.is_valid():
                event = form.save(commit=False)
                event.save()

#                log_defaults = {
#                    'event_id' : 432000,
#                    'event_data': '%s (%d) edited by %s' % (event._meta.object_name, event.pk, request.user),
#                    'description': '%s edited' % event._meta.object_name,
#                    'user': request.user,
#                    'request': request,
#                    'instance': event,
#                }

#                EventLog.objects.log(**log_defaults)

                
                # remove all permissions on the object
                ObjectPermission.objects.remove_all(event)
                
                # assign new permissions
                user_perms = form.cleaned_data['user_perms']
                if user_perms: ObjectPermission.objects.assign(user_perms, event)               
                # assign creator permissions
                ObjectPermission.objects.assign(event.creator, event) 

                messages.add_message(request, messages.INFO, 'Successfully updated %s' % event)
                
                # send notification to administrators
                if notification:
                    extra_context = {
                        'object': event,
                        'request': request,
                    }
                    notification.send(get_administrators(),'event_edited', extra_context)
                                                                             
                return HttpResponseRedirect(reverse('event', args=[event.pk]))             
        else:
            form = form_class(instance=event, user=request.user)

        return render_to_response(template_name, {'event': event, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="events/edit-meta.html"):

    # check permission
    event = get_object_or_404(Event, pk=id)
    if not request.user.has_perm('events.change_event', event):
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

def edit_place(request):
    pass

def edit_sponsor(request):
    pass

def edit_speaker(request):
    pass

def edit_organizer(request):
    pass

def edit_registration(request, event_id=0, form_class=Reg8nEditForm, template_name="events/reg8n/edit.html"):
#    from events.models import PaymentPeriod

    # check permission
    event = get_object_or_404(Event, pk=event_id)
    if not request.user.has_perm('events.change_event', event):
        raise Http403

    try:
        reg8n_config = RegistrationConfiguration.objects.get(event=event)
    except:
        defaults = {
            'event': event,
            'early_price':10,
            'regular_price':10,
            'late_price':10,
            'early_dt': datetime.now(),
            'regular_dt': datetime.now(),
            'late_dt': datetime.now(),
            'limit': 100,
         }
        reg8n_config = RegistrationConfiguration.objects.create(**defaults)

    if request.method == "POST":

        form = form_class(request.POST, instance=reg8n_config)

        if form.is_valid():
            # get variables
            reg8n_config = form.save(commit=False)
            payment_method = form.cleaned_data['payment_method']
            reg8n_config.save()

            # update payment methods available
            reg8n_config.payment_method = payment_method

    else:
        # TODO: will not work off of instance=event
        # this form-class is not attached to a model
        form = form_class(instance=reg8n_config)

    return render_to_response(template_name, {'event':event,'form':form}, 
        context_instance=RequestContext(request))

@login_required
def add(request, form_class=EventForm, template_name="events/add.html"):
    if request.user.has_perm('events.add_event'):
        if request.method == "POST":

            form = form_class(request.POST, user=request.user)
            if form.is_valid():           
                event = form.save(commit=False)
                # set up the user informationform_class
                event.creator = request.user
                event.creator_username = request.user.username
                event.owner = request.user
                event.owner_username = request.user.username
                event.save()
 
                log_defaults = {
                    'event_id' : 431000,
                    'event_data': '%s (%d) added by %s' % (event._meta.object_name, event.pk, request.user),
                    'description': '%s added' % event._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': event,
                }
                EventLog.objects.log(**log_defaults)
                               
                # assign permissions for selected users
                user_perms = form.cleaned_data['user_perms']
                if user_perms: ObjectPermission.objects.assign(user_perms, event)
                # assign creator permissions
                ObjectPermission.objects.assign(event.creator, event) 
                
                messages.add_message(request, messages.INFO, 'Successfully added %s' % event)
                
                # send notification to administrators
#                if notification:
#                    extra_context = {
#                        'object': event,
#                        'request': request,
#                    }
#                    notification.send(get_administrators(),'event_added', extra_context)
                    
                return HttpResponseRedirect(reverse('event', args=[event.pk]))
        else:
            form = form_class(user=request.user)
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def delete(request, id, template_name="events/delete.html"):
    event = get_object_or_404(Event, pk=id)

    if request.user.has_perm('events.delete_event'):   
        if request.method == "POST":
            log_defaults = {
                'event_id' : 433000,
                'event_data': '%s (%d) deleted by %s' % (event._meta.object_name, event.pk, request.user),
                'description': '%s deleted' % event._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': event,
            }
            
            EventLog.objects.log(**log_defaults)

            messages.add_message(request, messages.INFO, 'Successfully deleted %s' % event)

#            # send notification to administrators
#            if notification:
#                extra_context = {
#                    'object': event,
#                    'request': request,
#                }
#                notification.send(get_administrators(),'event_deleted', extra_context)
                            
            event.delete()
                                    
            return HttpResponseRedirect(reverse('event.search'))
    
        return render_to_response(template_name, {'event': event}, 
            context_instance=RequestContext(request))
    else:
        raise Http403# Create your views here.

@login_required
def register(request, event_id=0, form_class=Reg8nForm, template_name="events/reg8n/register.html"):
        event = get_object_or_404(Event, pk=event_id)
        
        if not RegistrationConfiguration.objects.filter(event=event).exists():
            raise Http404

        if request.method == "POST":
            form = form_class(event_id, request.POST)
            if form.is_valid():

                user_account = request.user
                user_profile = request.user.get_profile()

                try: # update registration
                    reg8n = Registration.objects.get(
                        event=event, creator=request.user, owner=request.user)
                    reg8n.payment_method = form.cleaned_data['payment_method']
                    reg8n.amount_paid = form.cleaned_data['price']

                except: # add registration
                    reg8n = Registration.objects.create(
                        event = event, 
                        creator = request.user, 
                        owner = request.user,
                        payment_method = form.cleaned_data['payment_method'],
                        amount_paid = form.cleaned_data['price']
                    )

                # get or create registrant
                registrant = reg8n.registrant_set.get_or_create(user=user_account)[0]

                # update registrant information
                registrant.name = '%s %s' % (user_account.first_name, user_account.last_name)
                registrant.mail_name = user_profile.display_name
                registrant.address = user_profile.address
                registrant.city = user_profile.city
                registrant.state = user_profile.state
                registrant.zip = user_profile.zipcode
                registrant.country = user_profile.country
                registrant.phone = user_profile.phone
                registrant.email = user_profile.email
                registrant.company_name = user_profile.company
                registrant.save()

                # save registration
                reg8n.save()

                response = HttpResponseRedirect(reverse('event.register.confirm', args=(event_id)))
            else:
                response = render_to_response(template_name, {'event':event, 'form':form}, 
                context_instance=RequestContext(request))
        else:
            form = form_class(event_id)
            response = render_to_response(template_name, {'event':event, 'form':form}, 
                context_instance=RequestContext(request))

        return response

def month_view(request, year=None, month=None, template_name='events/month-view.html'):

    year = int(year)
    month = int(month)

    calendar.setfirstweekday(calendar.SUNDAY)
    Calendar = calendar.Calendar

    # TODO: cleaner way
    next_month = (month+1)%13
    next_year = year
    if next_month == 0:
        next_month = 1
        next_year += 1

    # TODO: cleaner way
    prev_month = (month-1)%13
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    next_month_url = reverse('event.month', args=(next_year, next_month))
    prev_month_url = reverse('event.month', args=(prev_year, prev_month))

    month_names = calendar.month_name[month-1:month+2]
    weekdays = calendar.weekheader(10).split()
    month = Calendar(calendar.SUNDAY).monthdatescalendar(year, month)

    return render_to_response(template_name, { 
        'month':month,
        'prev_month_url':prev_month_url,
        'next_month_url':next_month_url,
        'month_names':month_names,
        'year':year,
        'weekdays':weekdays,
        }, 
        context_instance=RequestContext(request))

def day_view(request, year=None, month=None, day=None, template_name='events/day-view.html'):
    calendar = None

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
        }, 
        context_instance=RequestContext(request))


@login_required
def register_confirm(request, event_id=0, template_name="events/reg8n/register-confirm.html"):
        event = get_object_or_404(Event, pk=event_id)
        return render_to_response(template_name, {'event':event}, 
            context_instance=RequestContext(request))

@login_required
def registrant_search(request, event_id=0, template_name='events/registrants/search.html'):
    query = request.GET.get('q', None)

    event = get_object_or_404(Event, pk=event_id)
    registrants = Registrant.objects.search(query, user=request.user, event=event)

    return render_to_response(template_name, {'event':event, 'registrants':registrants}, 
        context_instance=RequestContext(request))

@login_required
def registrant_details(request, id=0, template_name='events/registrants/details.html'):
    registrant = get_object_or_404(Registrant, pk=id)
    
    if request.user.has_perm('registrans.view_registrant', registrant):
        return render_to_response(template_name, {'registrant': registrant}, 
            context_instance=RequestContext(request))
    else:
        raise Http403



