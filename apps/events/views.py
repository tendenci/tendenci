from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from base.http import Http403
from events.models import Event, RegistrationConfiguration
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
            form = form_class(request.POST, instance=event)
            if form.is_valid():
                event = form.save(commit=False)
                event.save()

                log_defaults = {
                    'event_id' : 432000,
                    'event_data': '%s (%d) edited by %s' % (event._meta.object_name, event.pk, request.user),
                    'description': '%s edited' % event._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': event,
                }
                EventLog.objects.log(**log_defaults)
                
                # remove all permissions on the object
                ObjectPermission.objects.remove_all(event)
                
#                # assign new permissions
#                user_perms = form.cleaned_data['user_perms']
#                if user_perms: ObjectPermission.objects.assign(user_perms, event)               
#                # assign creator permissions
#                ObjectPermission.objects.assign(event.creator, event) 
                
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
            form = form_class(instance=event)

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

def edit_registration(request, event_id=None, form_class=Reg8nEditForm, template_name="events/reg8n/edit.html"):
#    from events.models import PaymentPeriod
    from datetime import datetime

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
        form = form_class(request.POST)
        if form.is_valid():

            # get variables
            payment_methods = form.cleaned_data['payment_methods']
#            early_reg8n_price = form.cleaned_data['early_reg8n_price']
#            reg8n_price = form.cleaned_data['reg8n_price']
#            late_reg8n_price = form.cleaned_data['late_reg8n_price']

            reg8n_config.payment_methods = payment_methods

            # TODO: save the registration configuration
            # TODO: pull registration configuration (when re-editing)

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
            form = form_class(request.POST)
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
                               
#                # assign permissions for selected users
#                user_perms = form.cleaned_data['user_perms']
#                if user_perms: ObjectPermission.objects.assign(user_perms, event)
#                # assign creator permissions
#                ObjectPermission.objects.assign(event.creator, event) 
                
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
            form = form_class()
           
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

        if request.method == "POST":
            form = form_class(event_id, request.POST)
            if form.is_valid():

                # TODO: add them to registration here
                # TODO: check for duplicate registrations

                response = HttpResponseRedirect(reverse('event.register.confirm', args=(event_id)))
            else:
                response = render_to_response(template_name, {'event':event, 'form':form}, 
                context_instance=RequestContext(request))
        else:
            form = form_class(event_id)
            response = render_to_response(template_name, {'event':event, 'form':form}, 
                context_instance=RequestContext(request))

        return response

@login_required
def register_confirm(request, event_id=0, template_name="events/reg8n/register-confirm.html"):
        event = get_object_or_404(Event, pk=event_id)
        return render_to_response(template_name, {'event':event}, 
            context_instance=RequestContext(request))



