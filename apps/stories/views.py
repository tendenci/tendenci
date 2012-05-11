import os.path

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages

from base.http import Http403
from perms.utils import (has_perm, update_perms_and_save,
    get_query_filters, has_view_perm, is_admin)
from event_logs.models import EventLog
from site_settings.utils import get_setting
from theme.shortcuts import themed_response as render_to_response
from exports.tasks import TendenciExportTask

from stories.models import Story
from stories.forms import StoryForm, UploadStoryImageForm


def details(request, id=None, template_name="stories/view.html"):
    if not id: return HttpResponseRedirect(reverse('story.search'))
    story = get_object_or_404(Story, pk=id)
    
    if not has_view_perm(request.user,'stories.view_story', story):
        raise Http403

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
    
def print_details(request, id, template_name="stories/print_details.html"):
    story = get_object_or_404(Story, pk=id)
    if not has_view_perm(request.user,'stories.view_story', story):
        raise Http403

    log_defaults = {
        'event_id' : 1060501,
        'event_data': '%s (%d) print viewed by %s' % (story._meta.object_name, story.pk, request.user),
        'description': '%s print viewed' % story._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': story,
    }
    EventLog.objects.log(**log_defaults)

    return render_to_response(template_name, {'story': story}, 
        context_instance=RequestContext(request))
    
def search(request, template_name="stories/search.html"):
    """
    This page lists out all stories from newest to oldest.
    If a search index is available, this page will also
    have the option to search through stories.
    """
    has_index = get_setting('site', 'global', 'searchindex')
    query = request.GET.get('q', None)

    if has_index and query:
        stories = Story.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'stories.view_story')
        stories = Story.objects.filter(filters).distinct()
        if request.user.is_authenticated():
            stories = stories.select_related()
        stories = stories.order_by('-create_dt')

    EventLog.objects.log(**{
        'event_id' : 1060400,
        'event_data': '%s searched by %s' % ('Story', request.user),
        'description': '%s searched' % 'Story',
        'user': request.user,
        'request': request,
        'source': 'stories'
    })

    return render_to_response(template_name, {'stories':stories}, 
        context_instance=RequestContext(request))

def search_redirect(request):
    return HttpResponseRedirect(reverse('stories'))

@login_required   
def add(request, form_class=StoryForm, template_name="stories/add.html"):
    
    if has_perm(request.user,'stories.add_story'):    
        if request.method == "POST":
            form = form_class(request.POST, request.FILES, user=request.user)
            if form.is_valid():           
                story = form.save(commit=False)
                story = update_perms_and_save(request, form, story)

                # save photo
                photo = form.cleaned_data['photo_upload']
                if photo: story.save(photo=photo)

                log_defaults = {
                    'event_id' : 1060100,
                    'event_data': '%s (%d) added by %s' % (story._meta.object_name, story.pk, request.user),
                    'description': '%s added' % story._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': story,
                }
                EventLog.objects.log(**log_defaults)
                
                messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % story) 
                
                return HttpResponseRedirect(reverse('story', args=[story.pk]))
            else:
                from pprint import pprint
                pprint(form.errors.items())
        else:
            form = form_class(user=request.user)

            tags = request.GET.get('tags', '')
            if tags:
                form.fields['tags'].initial = tags

    else:
        raise Http403

    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
    
@login_required
def edit(request, id, form_class=StoryForm, template_name="stories/edit.html"):
    story = get_object_or_404(Story, pk=id)

    if has_perm(request.user,'stories.change_story', story):
        if request.method == "POST":
            form = form_class(request.POST, request.FILES,
                              instance=story, user=request.user)
            if form.is_valid():

                story = form.save(commit=False)
                story = update_perms_and_save(request, form, story)

                # save photo
                photo = form.cleaned_data['photo_upload']
                if photo: story.save(photo=photo)

                log_defaults = {
                    'event_id' : 1060200,
                    'event_data': '%s (%d) edited by %s' % (story._meta.object_name, story.pk, request.user),
                    'description': '%s edited' % story._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': story,
                }
                EventLog.objects.log(**log_defaults)
                
                messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % story)
                
                redirect_to = request.REQUEST.get('next', '')
                if redirect_to:
                    return HttpResponseRedirect(redirect_to)
                else:
                    return redirect('story', id=story.pk)             
        else:
            form = form_class(instance=story, user=request.user)

    else:
        raise Http403

    return render_to_response(template_name, {'story': story, 'form':form }, 
        context_instance=RequestContext(request))

@login_required
def delete(request, id, template_name="stories/delete.html"):
    story = get_object_or_404(Story, pk=id)

    if has_perm(request.user,'stories.delete_story'):   
        if request.method == "POST":
            log_defaults = {
                'event_id' : 1060300,
                'event_data': '%s (%d) deleted by %s' % (story._meta.object_name, story.pk, request.user),
                'description': '%s deleted' % story._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': story,
            }
            EventLog.objects.log(**log_defaults)
            
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % story)
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
        form = form_class(user=request.user)
    return render_to_response(template_name, {'form':form, 'story': story}, 
            context_instance=RequestContext(request))
    
@login_required
def export(request, template_name="stories/export.html"):
    """Export Stories"""
    
    if not is_admin(request.user):
        raise Http403
    
    if request.method == 'POST':
        # initilize initial values
        file_name = "stories.xls"
        fields = [
            'guid',
            'title',
            'content',
            'syndicate',
            'full_story_link',
            'start_dt',
            'end_dt',
            'expires',
            'ncsortorder',
            'entity',
            'tags',
            'categories',
        ]
        
        if not settings.CELERY_IS_ACTIVE:
            # if celery server is not present 
            # evaluate the result and render the results storie
            result = TendenciExportTask()
            response = result.run(Story, fields, file_name)
            return response
        else:
            result = TendenciExportTask.delay(Story, fields, file_name)
            return redirect('export.status', result.task_id)
        
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
