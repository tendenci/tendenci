# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from stories.models import Story
from stories.forms import StoryForm

def index(request, id=None, template_name="stories/view.html"):
    if not id: return HttpResponseRedirect(reverse('story.search'))
    story = get_object_or_404(Story, pk=id)
    return render_to_response(template_name, {'story': story}, 
        context_instance=RequestContext(request))

def search(request, template_name="stories/search.html"):
    stories = Story.objects.all()
    return render_to_response(template_name, {'stories':stories}, 
        context_instance=RequestContext(request))
    
@login_required   
def add(request, template_name="stories/add.html"):
    if request.method == "POST":
        form = StoryForm(request.POST, request.user)
        if form.is_valid():
            story = form.save(commit=False)
            story.user = request.user
            story.creator = request.user
            story.creator_username = request.user.username
            story.owner = request.user
            story.owner_username = request.user.username
            story.save()
            # back to view
            return HttpResponseRedirect(reverse('story', args=[story.id]))
    else:
        form  = StoryForm()
            
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
    
@login_required
def edit(request, id, template_name="stories/edit.html"):
    story = get_object_or_404(Story, pk=id)
    form = StoryForm(instance=story)

    if request.method == "POST":
        form = StoryForm(request.POST, request.user, instance=story)
        if form.is_valid():
            story = form.save(commit=False)
            story.owner = request.user
            story.owner_username = request.user.username
            story.save()
            return HttpResponseRedirect(reverse('story', args=[story.id]))

    return render_to_response(template_name, {'story': story, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def delete(request, id, template_name="stories/delete.html"):
    story = get_object_or_404(Story, pk=id)

    if request.method == "POST":
        story.delete()
        return HttpResponseRedirect(reverse('story.search'))

    return render_to_response(template_name, {'story': story}, 
        context_instance=RequestContext(request))