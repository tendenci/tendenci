import os.path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from base.http import Http403
from stories.models import Story
from stories.forms import StoryForm, UploadStoryImageForm
from perms.models import ObjectPermission
from event_logs.models import EventLog

def index(request, id=None, template_name="stories/view.html"):
    if not id: return HttpResponseRedirect(reverse('story.search'))
    story = get_object_or_404(Story, pk=id)
    
    if not story.allow_view_by(request.user): raise Http403

    log_defaults = {
        'event_id' : 1060500,
        'event_data': '%s (%d) viewed by %s' % (story._meta.object_name, story.pk, request.user),
        'description': '%s viewed' % story._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': story,
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'story': story}, 
        context_instance=RequestContext(request))
    
# get the latest image name
def get_latest_image_name(images_path):
    latest_image = ""
    if os.path.isdir(images_path):
        image_list = os.listdir(images_path)
        
        if image_list <> []:
            image_full_path_list = [images_path+'/'+image_name for image_name in image_list]
            
            latest_image = image_list[0]
            mtime = os.path.getmtime(image_full_path_list[0])
            
            for i in range(1, len(image_full_path_list)):
                if mtime < os.path.getmtime(image_full_path_list[i]):
                    latest_image = image_list[i]
                    mtime = os.path.getmtime(image_full_path_list[i])
    return latest_image
        
    

def search(request, template_name="stories/search.html"):
    query = request.GET.get('q', None)
    stories = Story.objects.search(query)

    log_defaults = {
        'event_id' : 1060400,
        'event_data': '%s searched by %s' % ('Story', request.user),
        'description': '%s searched' % 'Story',
        'user': request.user,
        'request': request,
        'source': 'stories'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'stories':stories}, 
        context_instance=RequestContext(request))
    
@login_required   
def add(request, form_class=StoryForm, template_name="stories/add.html"):
    # permission check
    story = Story()
    if not story.allow_add_by(request.user): raise Http403
    
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if form.is_valid():           
            story = form.save(commit=False)
            # set up the user information
            story.allow_anonymous_view = 1
            story.creator = request.user
            story.creator_username = request.user.username
            story.owner = request.user
            story.owner_username = request.user.username
            story.save()

            log_defaults = {
                'event_id' : 1060100,
                'event_data': '%s (%d) added by %s' % (story._meta.object_name, story.pk, request.user),
                'description': '%s added' % story._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': story,
            }
            EventLog.objects.log(**log_defaults)
            
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
    
@login_required
def edit(request, id, form_class=StoryForm, template_name="stories/edit.html"):
    story = get_object_or_404(Story, pk=id)
    # permission check
    if not story.allow_edit_by(request.user): raise Http403
    # temporarily - need to use file module to store the image
    imagepath = os.path.join(settings.MEDIA_ROOT, 'stories/'+str(story.id))
    image_name = story.get_latest_image_name(imagepath)

    if request.method == "POST":
        form = form_class(request.user, request.POST, instance=story)
        if form.is_valid():
            story = form.save(commit=False)
            story.save()
            
            log_defaults = {
                'event_id' : 1060200,
                'event_data': '%s (%d) edited by %s' % (story._meta.object_name, story.pk, request.user),
                'description': '%s edited' % story._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': story,
            }
            EventLog.objects.log(**log_defaults)
    
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
    
    return render_to_response(template_name, {'story': story, 'form':form, 'image_name':image_name}, 
        context_instance=RequestContext(request))


@login_required
def delete(request, id, template_name="stories/delete.html"):
    story = get_object_or_404(Story, pk=id)
    # permission check
    if not story.allow_edit_by(request.user): raise Http403

    if request.user.has_perm('stories.delete_stories'):   
        if request.method == "POST":
            # delete files first
            imagepath = os.path.join(settings.MEDIA_ROOT, 'stories/'+str(story.id))
            if os.path.isdir(imagepath):
                for file in os.listdir(imagepath):
                    os.remove(os.path.join(imagepath+'/' + file))
                os.rmdir(imagepath)

            log_defaults = {
                'event_id' : 1060300,
                'event_data': '%s (%d) deleted by %s' % (story._meta.object_name, story.pk, request.user),
                'description': '%s deleted' % story._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': story,
            }
            EventLog.objects.log(**log_defaults)
            
            story.delete()
            
            
            return HttpResponseRedirect(reverse('story.search'))
    
        return render_to_response(template_name, {'story': story}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
 
@login_required   
def upload(request, id, form_class=UploadStoryImageForm, 
                template_name="stories/upload.html"):
    story = get_object_or_404(Story, pk=id)
    # permission check
    if not story.allow_edit_by(request.user): raise Http403
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data['file']
            imagename = data.name
            imagepath = os.path.join(settings.MEDIA_ROOT, 'stories/'+str(story.id))
            if not os.path.isdir(imagepath):
                os.makedirs(imagepath)
            fd = open(imagepath + '/' + imagename, 'wb+')
            for chunk in data.chunks():
                fd.write(chunk)
            fd.close()
            #filelog(mode='wb+', filename=imagename, path=imagepath)
            return HttpResponseRedirect(reverse('story', args=[story.pk]))
    else:
        form = form_class()
    return render_to_response(template_name, {'form':form, 'story': story}, 
            context_instance=RequestContext(request))
    
            
            
            