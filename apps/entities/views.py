from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from base.http import Http403
from entities.models import Entity
from entities.forms import EntityForm, EntityEditForm
from entities.permissions import EntityPermission

def index(request, id=None, template_name="entities/view.html"):
    if not id: return HttpResponseRedirect(reverse('entity.search'))
    entity = get_object_or_404(Entity, pk=id)
    auth = EntityPermission(request.user)
    
    if auth.view(entity): # TODO : maybe make this a decorator
        return render_to_response(template_name, {'entity': entity}, 
            context_instance=RequestContext(request))
    else:
        raise Http403 # TODO : change where this goes

def search(request, template_name="entities/search.html"):
    entities = Entity.objects.all()
    return render_to_response(template_name, {'entities':entities}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="entities/print-view.html"):
    entity = get_object_or_404(Entity, pk=id)
    auth = EntityPermission(request.user)
     
    if auth.view(entity): # TODO : maybe make this a decorator
        return render_to_response(template_name, {'entity': entity}, 
            context_instance=RequestContext(request))
    else:
        raise Http403 # TODO : change where this goes
    
@login_required
def edit(request, id, form_class=EntityEditForm, template_name="entities/edit.html"):
    entity = get_object_or_404(Entity, pk=id)
    auth = EntityPermission(request.user)
    
    if auth.edit(entity): # TODO : maybe make this a decorator    
        if request.method == "POST":
            form = form_class(request.user, request.POST, instance=entity)
            if form.is_valid():
                original_owner = entity.owner
                entity = form.save(commit=False)
                entity.save()
                
                # assign creator permissions
                auth.assign(content_object=entity)   
 
                # assign owner permissions
                if entity.owner != original_owner:    
                    auth = EntityPermission(entity.owner)
                    auth.assign(content_object=entity)  
                    if original_owner != entity.creator:
                        auth = EntityPermission(original_owner)
                        auth.remove(content_object=entity)
                               
                return HttpResponseRedirect(reverse('entity', args=[entity.pk]))             
        else:
            form = form_class(request.user, instance=entity)

        return render_to_response(template_name, {'entity': entity, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403 # TODO : change where this goes

@login_required
def add(request, form_class=EntityForm, template_name="entities/add.html"):
    auth = EntityPermission(request.user)
    
    if auth.add(): # TODO : maybe make this a decorator   
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
                
                # assign creator and owner permissions
                auth.assign(content_object=entity)
                
                return HttpResponseRedirect(reverse('entity', args=[entity.pk]))
        else:
            form = form_class(request.user)
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403 # TODO : change where this goes
    
@login_required
def delete(request, id, template_name="entities/delete.html"):
    entity = get_object_or_404(Entity, pk=id)

    auth = EntityPermission(request.user)
    if auth.delete(entity): # TODO : make this a decorator    
        if request.method == "POST":
            entity.delete()
            return HttpResponseRedirect(reverse('entity.search'))
    
        return render_to_response(template_name, {'entity': entity}, 
            context_instance=RequestContext(request))
    else:
        raise Http404 # TODO : change where this goes