from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from base.http import Http403
from entities.models import Entity
from entities.forms import EntityForm
from perms.models import ObjectPermission
from event_logs.models import EventLog
from perms.utils import is_admin
from perms.utils import has_perm

def index(request, id=None, template_name="entities/view.html"):
    if not id: return HttpResponseRedirect(reverse('entity.search'))
    entity = get_object_or_404(Entity, pk=id)
   
    if has_perm(request.user,'entities.view_entity',entity):
        log_defaults = {
            'event_id' : 295000,
            'event_data': '%s (%d) viewed by %s' % (entity._meta.object_name, entity.pk, request.user),
            'description': '%s viewed' % entity._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': entity,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'entity': entity}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="entities/search.html"):
    query = request.GET.get('q', None)
    is_an_admin = is_admin(request.user)
    entities = Entity.objects.search(query, user=request.user, is_admin=is_an_admin)

    log_defaults = {
        'event_id' : 294000,
        'event_data': '%s searched by %s' % ('Entity', request.user),
        'description': '%s searched' % 'Entity',
        'user': request.user,
        'request': request,
        'source': 'entities'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'entities':entities}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="entities/print-view.html"):
    entity = get_object_or_404(Entity, pk=id)
     
    if has_perm(request.user,'entities.view_entity',entity):
        log_defaults = {
            'event_id' : 295000,
            'event_data': '%s (%d) viewed by %s' % (entity._meta.object_name, entity.pk, request.user),
            'description': '%s viewed' % entity._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': entity,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'entity': entity}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def add(request, form_class=EntityForm, template_name="entities/add.html"):    
    if has_perm(request.user,'entities.add_entity'):   
        if request.method == "POST":
            form = form_class(request.POST, user=request.user)
            if form.is_valid():
                entity = form.save(commit=False)
                
                # set up the user information
                entity.creator = request.user
                entity.creator_username = request.user.username
                entity.owner = request.user
                entity.owner_username = request.user.username          

                # set up user permission
                entity.allow_user_view, entity.allow_user_edit = form.cleaned_data['user_perms']
                     
                entity.save() # get pk

                # assign permissions for selected groups
                ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], entity)
                # assign creator permissions
                ObjectPermission.objects.assign(entity.creator, entity) 

                entity.save() # update search-index w/ permissions

                log_defaults = {
                    'event_id' : 291000,
                    'event_data': '%s (%d) added by %s' % (entity._meta.object_name, entity.pk, request.user),
                    'description': '%s added' % entity._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': entity,
                }
                EventLog.objects.log(**log_defaults)
                
                messages.add_message(request, messages.INFO, 'Successfully added %s' % entity)
                
                return HttpResponseRedirect(reverse('entity', args=[entity.pk]))
        else:
            form = form_class(user=request.user)
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def edit(request, id, form_class=EntityForm, template_name="entities/edit.html"):
    entity = get_object_or_404(Entity, pk=id)

    if has_perm(request.user,'entities.change_entity',entity):   
        if request.method == "POST":
            form = form_class(request.POST, instance=entity, user=request.user)
            if form.is_valid():               
                entity = form.save(commit=False)

                # set up user permission
                entity.allow_user_view, entity.allow_user_edit = form.cleaned_data['user_perms']
                
                # assign permissions
                ObjectPermission.objects.remove_all(entity)
                ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], entity)
                ObjectPermission.objects.assign(entity.creator, entity) 

                entity.save()

                log_defaults = {
                    'event_id' : 292000,
                    'event_data': '%s (%d) edited by %s' % (entity._meta.object_name, entity.pk, request.user),
                    'description': '%s edited' % entity._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': entity,
                }
                EventLog.objects.log(**log_defaults)                           

                return HttpResponseRedirect(reverse('entity', args=[entity.pk]))             
        else:
            form = form_class(instance=entity, user=request.user)

        return render_to_response(template_name, {'entity': entity, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
   
@login_required
def delete(request, id, template_name="entities/delete.html"):
    entity = get_object_or_404(Entity, pk=id)

    if has_perm(request.user,'entities.delete_entity'):     
        if request.method == "POST":
            log_defaults = {
                'event_id' : 293000,
                'event_data': '%s (%d) deleted by %s' % (entity._meta.object_name, entity.pk, request.user),
                'description': '%s deleted' % entity._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': entity,
            }
            EventLog.objects.log(**log_defaults)
            messages.add_message(request, messages.INFO, 'Successfully deleted %s' % entity)
            entity.delete()
            return HttpResponseRedirect(reverse('entity.search'))
    
        return render_to_response(template_name, {'entity': entity}, 
            context_instance=RequestContext(request))
    else:
        raise Http403