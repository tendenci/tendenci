from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from releases.models import Release
from releases.forms import ReleaseForm
from releases.permissions import ReleasePermission
from base.auth import Authorize


def index(request, id=None, template_name="releases/view.html"):
    if not id: return HttpResponseRedirect(reverse('release.search'))
    release = get_object_or_404(Release, pk=id)
    return render_to_response(template_name, {'release': release}, 
        context_instance=RequestContext(request))

def search(request, template_name="releases/search.html"):
    releases = Release.objects.all()
    return render_to_response(template_name, {'releases':releases}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="releases/print-view.html"):
    release = get_object_or_404(Release, pk=id)
    return render_to_response(template_name, {'release': release}, 
        context_instance=RequestContext(request))

@login_required
def edit(request, id, template_name="releases/edit.html"):
    release = get_object_or_404(Release, pk=id)
    form = ReleaseForm(instance=release)

    if request.method == "POST":
        form = ReleaseForm(request.POST, request.user, instance=release)
        if form.is_valid():
            release = form.save()

    return render_to_response(template_name, {'release': release, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def delete(request, id, template_name="releases/delete.html"):
    release = get_object_or_404(Release, pk=id)

    print "Release ID: " + id
    print release.headline

    if request.method == "POST":
        release.delete()
        return HttpResponseRedirect(reverse('release.search'))

    return render_to_response(template_name, {'release': release}, 
        context_instance=RequestContext(request))