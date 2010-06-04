from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import render_to_403
from stories.models import Story
from stories.forms import StoryForm
from perms.models import ObjectPermission

def index(request, id=None, template_name="stories/view.html"):
    if not id: return HttpResponseRedirect(reverse('story.search'))
    story = get_object_or_404(Story, pk=id)
    if request.user.has_perm('stories.view_story', story):
        return render_to_response(template_name, {'story': story}, 
            context_instance=RequestContext(request))
    else:
        return render_to_403()
    

def search(request, template_name="stories/search.html"):
    stories = Story.objects.all()
    return render_to_response(template_name, {'stories':stories}, 
        context_instance=RequestContext(request))
    
@login_required   
def add(request, form_class=StoryForm, template_name="stories/add.html"):
    if request.user.has_perm('stories.add_story'):
        if request.method == "POST":
            form = form_class(request.user, request.POST)
            if form.is_valid():           
                story = form.save(commit=False)
                # set up the user information
                story.creator = request.user
                story.creator_username = request.user.username
                story.owner = request.user
                story.owner_username = request.user.username
                story.save()
                
                # assign permissions for selected users
                user_perms = form.cleaned_data['user_perms']
                if user_perms:
                    ObjectPermission.objects.assign(user_perms, story)
                
                # assign creator permissions
                ObjectPermission.objects.assign(story.creator, story) 
                
                return HttpResponseRedirect(reverse('story', args=[story.pk]))
        else:
            form = form_class(request.user)
        
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        return render_to_403()
    
@login_required
def edit(request, id, form_class=StoryForm, template_name="stories/edit.html"):
    story = get_object_or_404(Story, pk=id)

    if request.user.has_perm('stories.change_story', story):    
        if request.method == "POST":
            form = form_class(request.user, request.POST, instance=story)
            if form.is_valid():
                story = form.save(commit=False)
                story.save()

                # remove all permissions on the object
                ObjectPermission.objects.remove_all(story)
                
                # assign new permissions
                user_perms = form.cleaned_data['user_perms']
                if user_perms:
                    ObjectPermission.objects.assign(user_perms, story)               
 
                # assign creator permissions
                ObjectPermission.objects.assign(story.creator, story) 
                                                              
                return HttpResponseRedirect(reverse('story', args=[story.pk]))             
        else:
            form = form_class(request.user, instance=story)

        return render_to_response(template_name, {'story': story, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        return render_to_403()

@login_required
def delete(request, id, template_name="stories/delete.html"):
    story = get_object_or_404(Story, pk=id)

    if request.user.has_perm('stories.delete_stories'):   
        if request.method == "POST":
            story.delete()
            return HttpResponseRedirect(reverse('story.search'))
    
        return render_to_response(template_name, {'story': story}, 
            context_instance=RequestContext(request))
    else:
        return render_to_403()