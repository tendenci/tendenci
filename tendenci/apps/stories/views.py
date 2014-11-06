import os.path

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.base.http import Http403
from tendenci.apps.base.utils import checklist_update
from tendenci.apps.perms.utils import (has_perm, update_perms_and_save,
    get_query_filters, has_view_perm)
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.shortcuts import themed_response as render_to_response
from tendenci.apps.exports.utils import run_export_task

from tendenci.apps.stories.models import Story
from tendenci.apps.stories.forms import StoryForm
from tendenci.apps.perms.utils import assign_files_perms


@is_enabled('stories')
def details(request, id=None, template_name="stories/view.html"):
    if not id: return HttpResponseRedirect(reverse('story.search'))
    story = get_object_or_404(Story, pk=id)

    if not has_view_perm(request.user,'stories.view_story', story):
        raise Http403

    EventLog.objects.log(instance=story)

    return render_to_response(template_name, {'story': story},
        context_instance=RequestContext(request))


@is_enabled('stories')
def print_details(request, id, template_name="stories/print_details.html"):
    story = get_object_or_404(Story, pk=id)
    if not has_view_perm(request.user,'stories.view_story', story):
        raise Http403

    EventLog.objects.log(instance=story)

    return render_to_response(template_name, {'story': story},
        context_instance=RequestContext(request))


@is_enabled('stories')
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

    EventLog.objects.log()

    return render_to_response(template_name, {'stories':stories},
        context_instance=RequestContext(request))

def search_redirect(request):
    return HttpResponseRedirect(reverse('stories'))


@is_enabled('stories')
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
                if photo:
                    story.save(photo=photo)
                    assign_files_perms(story, files=[story.image])

                if 'rotator' in story.tags:
                    checklist_update('add-story')

                messages.add_message(request, messages.SUCCESS, _('Successfully added %(str)s' % {'str': unicode(story)}))

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


@is_enabled('stories')
@login_required
def edit(request, id, form_class=StoryForm, template_name="stories/edit.html"):
    story = get_object_or_404(Story, pk=id)

    if has_perm(request.user,'stories.change_story', story):
        if request.method == "POST":
            form = form_class(request.POST, request.FILES,
                              instance=story, user=request.user)
            if form.is_valid():
                story = form.save(commit=False)

                # save photo
                photo = form.cleaned_data['photo_upload']
                if photo:
                    story.save(photo=photo)

                story = update_perms_and_save(request, form, story)

                messages.add_message(request, messages.SUCCESS, _('Successfully updated %(str)s' % {'str': unicode(story)}))

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


@is_enabled('stories')
@login_required
def delete(request, id, template_name="stories/delete.html"):
    story = get_object_or_404(Story, pk=id)

    if has_perm(request.user,'stories.delete_story'):
        if request.method == "POST":
            if story.image:
                # Delete story.image to prevent transaction issues.
                story.image.delete()
            story.delete()
            messages.add_message(request, messages.SUCCESS, _('Successfully deleted %(str)s' % {'str': unicode(story)}))

            return HttpResponseRedirect(reverse('story.search'))

        return render_to_response(template_name, {'story': story},
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('stories')
@login_required
def export(request, template_name="stories/export.html"):
    """Export Stories"""
    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        # initilize initial values
        file_name = "stories.csv"
        fields = [
            'guid',
            'title',
            'content',
            'syndicate',
            'full_story_link',
            'start_dt',
            'end_dt',
            'expires',
            'position',
            'entity',
            'tags',
            'categories',
        ]
        export_id = run_export_task('stories', 'story', fields)
        return redirect('export.status', export_id)

    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
