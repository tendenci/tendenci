from os.path import basename, join, abspath, dirname

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.core.files.images import ImageFile

from tendenci.apps.base.http import Http403
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.files.utils import get_image
from tendenci.apps.perms.utils import has_perm, has_view_perm, get_query_filters
from tendenci.apps.speakers.models import Speaker


def details(request, slug=None, template_name="speakers/view.html"):
    if not slug: return HttpResponseRedirect(reverse('speakers'))
    speaker = get_object_or_404(Speaker, slug=slug)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (speaker.status_detail).lower() != 'active' and (not request.user.profile.is_superuser):
        raise Http403

    if has_perm(request.user, 'speaker.view_speaker', speaker):
        EventLog.objects.log(instance=speaker)
        return render_to_response(template_name, {'speaker': speaker},
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="speakers/search.html"):
    """
    This page lists out all speakers from newest to oldest.
    If a search index is available, this page will also
    have the option to search through speakers.
    """
    has_index = get_setting('site', 'global', 'searchindex')
    query = request.GET.get('q', None)

    if has_index and query:
        speakers = Speaker.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'speakers.view_story')
        speakers = Speaker.objects.filter(filters).distinct()
        if request.user.is_authenticated():
            speakers = speakers.select_related()
    speakers = speakers.order_by('ordering')

    EventLog.objects.log()

    return render_to_response(template_name, {'speakers':speakers},
        context_instance=RequestContext(request))

def search_redirect(request):
    return HttpResponseRedirect(reverse('speakers'))
