from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from theme.shortcuts import themed_response as render_to_response
from base.http import Http403
from event_logs.models import EventLog
from perms.utils import has_perm, update_perms_and_save, is_admin
from locations.models import Location
from locations.forms import LocationForm
from locations.utils import get_coordinates

def index(request, id=None, template_name="locations/view.html"):
    if not id: return HttpResponseRedirect(reverse('location.search'))
    location = get_object_or_404(Location, pk=id)
    
    if has_perm(request.user,'locations.view_location',location):
        log_defaults = {
            'event_id' : 835000,
            'event_data': '%s (%d) viewed by %s' % (location._meta.object_name, location.pk, request.user),
            'description': '%s viewed' % location._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': location,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'location': location}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="locations/search.html"):
    query = request.GET.get('q', None)
    locations = Location.objects.search(query, user=request.user)
    locations = locations.order_by('-create_dt')

    log_defaults = {
        'event_id' : 834000,
        'event_data': '%s searched by %s' % ('Location', request.user),
        'description': '%s searched' % 'Location',
        'user': request.user,
        'request': request,
        'source': 'locations'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'locations':locations}, 
        context_instance=RequestContext(request))

def nearest(request, template_name="locations/nearest.html"):
    locations = []
    lat, lng = None, None
    query = request.GET.get('q')

    if query:
        lat, lng = get_coordinates(address=query)

    if all((lat,lng)):
        for location in Location.objects.search(user=request.user).load_all():
            location.object.distance = location.object.get_distance2(lat, lng)
            if location.object.distance != None:
                locations.append(location.object)
            locations.sort(key=lambda x: x.distance)

    log_defaults = {
        'event_id' : 834100,
        'event_data': '%s nearest to %s' % ('Location', request.user),
        'description': '%s nearest' % 'Location',
        'user': request.user,
        'request': request,
        'source': 'locations'
    }
    EventLog.objects.log(**log_defaults)

    return render_to_response(template_name, {
        'locations':locations,
        'origin': {'lat':lat,'lng':lng},
        }, context_instance=RequestContext(request))

def print_view(request, id, template_name="locations/print-view.html"):
    location = get_object_or_404(Location, pk=id)    

    log_defaults = {
        'event_id' : 835000,
        'event_data': '%s (%d) viewed by %s' % (location._meta.object_name, location.pk, request.user),
        'description': '%s viewed' % location._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': location,
    }
    EventLog.objects.log(**log_defaults)
       
    if has_perm(request.user,'locations.view_location',location):
        return render_to_response(template_name, {'location': location}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def edit(request, id, form_class=LocationForm, template_name="locations/edit.html"):
    location = get_object_or_404(Location, pk=id)

    if has_perm(request.user,'locations.change_location',location):    
        if request.method == "POST":
            form = form_class(request.POST, instance=location, user=request.user)
            if form.is_valid():
                location = form.save(commit=False)

                # update all permissions and save the model
                location = update_perms_and_save(request, form, location)

                log_defaults = {
                    'event_id' : 832000,
                    'event_data': '%s (%d) edited by %s' % (location._meta.object_name, location.pk, request.user),
                    'description': '%s edited' % location._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': location,
                }
                EventLog.objects.log(**log_defaults)               
                
                messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % location)
                                                              
                return HttpResponseRedirect(reverse('location', args=[location.pk]))             
        else:
            form = form_class(instance=location, user=request.user)

        return render_to_response(template_name, {'location': location, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def add(request, form_class=LocationForm, template_name="locations/add.html"):
    if has_perm(request.user,'locations.add_location'):
        if request.method == "POST":
            form = form_class(request.POST, user=request.user)
            if form.is_valid():           
                location = form.save(commit=False)

                # update all permissions and save the model
                location = update_perms_and_save(request, form, location)
 
                log_defaults = {
                    'event_id' : 831000,
                    'event_data': '%s (%d) added by %s' % (location._meta.object_name, location.pk, request.user),
                    'description': '%s added' % location._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': location,
                }
                EventLog.objects.log(**log_defaults)
                
                messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % location)
                
                return HttpResponseRedirect(reverse('location', args=[location.pk]))
        else:
            form = form_class(user=request.user)
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def delete(request, id, template_name="locations/delete.html"):
    location = get_object_or_404(Location, pk=id)

    if has_perm(request.user,'locations.delete_location'):   
        if request.method == "POST":
            log_defaults = {
                'event_id' : 833000,
                'event_data': '%s (%d) deleted by %s' % (location._meta.object_name, location.pk, request.user),
                'description': '%s deleted' % location._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': location,
            }
            
            EventLog.objects.log(**log_defaults)
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % location)
            location.delete()
                
            return HttpResponseRedirect(reverse('location.search'))
    
        return render_to_response(template_name, {'location': location}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
