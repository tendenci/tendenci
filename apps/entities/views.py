from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from entities.models import Entity
from entities.forms import EntityForm
from perms.models import ObjectPermission

def index(request, id=None, template_name="entities/view.html"):
    if not id: return HttpResponseRedirect(reverse('entity.search'))
    entity = get_object_or_404(Entity, pk=id)
    
    if request.user.has_perm('entities.view_entity', entity):
        return render_to_response(template_name, {'entity': entity}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="entities/search.html"):
    entities = Entity.objects.all()
    return render_to_response(template_name, {'entities':entities}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="entities/print-view.html"):
    entity = get_object_or_404(Entity, pk=id)
     
    if request.user.has_perm('entities.view_entity', entity):
        return render_to_response(template_name, {'entity': entity}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def edit(request, id, form_class=EntityForm, template_name="entities/edit.html"):
    entity = get_object_or_404(Entity, pk=id)

    if request.user.has_perm('entities.change_entity', entity):   
        if request.method == "POST":
            form = form_class(request.user, request.POST, instance=entity)
            if form.is_valid():
                
                entity = form.save(commit=False)
                entity.save()
                
                # remove all permissions on the object
                ObjectPermission.objects.remove_all(entity)
                
                # assign new permissions
                user_perms = form.cleaned_data['user_perms']
                if user_perms:
                    ObjectPermission.objects.assign(user_perms, entity)  
                               
                return HttpResponseRedirect(reverse('entity', args=[entity.pk]))             
        else:
            form = form_class(request.user, instance=entity)

        return render_to_response(template_name, {'entity': entity, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def add(request, form_class=EntityForm, template_name="entities/add.html"):    
    if request.user.has_perm('entities.add_entity'):   
        if request.method == "POST":
            form = form_class(request.user, request.POST)
            if form.is_valid():
                entity = form.save(commit=False)
                
                # set up the user information
                entity.creator = request.user
                entity.creator_username = request.user.username
                entity.owner = request.user
                entity.owner_username = request.user.username
                
                entity.save()
                
                # assign permissions for selected users
                user_perms = form.cleaned_data['user_perms']
                if user_perms:
                    ObjectPermission.objects.assign(user_perms, entity)
                
                # assign creator permissions
                ObjectPermission.objects.assign(entity.creator, entity) 
                
                return HttpResponseRedirect(reverse('entity', args=[entity.pk]))
        else:
            form = form_class(request.user)
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def delete(request, id, template_name="entities/delete.html"):
    entity = get_object_or_404(Entity, pk=id)

    if request.user.has_perm('entities.delete_entity'):     
        if request.method == "POST":
            entity.delete()
            return HttpResponseRedirect(reverse('entity.search'))
    
        return render_to_response(template_name, {'entity': entity}, 
            context_instance=RequestContext(request))
    else:
        raise Http403