from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from site_settings.utils import get_setting
from museums.models import Museum
from perms.utils import get_notice_recipients, has_perm, has_view_perm, get_query_filters
from event_logs.models import EventLog

from perms.utils import is_admin
from notification import models as notification

def details(request, slug=None, template_name="museums/detail.html"):
    if not slug: return HttpResponseRedirect(reverse('museums'))
    museum = get_object_or_404(Museum, slug=slug)
    
    if has_perm(request.user, 'museum.view_museum', museum):
        log_defaults = {
            'event_id' : 1140500,
            'event_data': '%s (%d) viewed by %s' % (museum._meta.object_name, museum.pk, request.user),
            'description': '%s viewed' % museum._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': museum,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'museum': museum}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="museums/search.html"):
    """
    This page lists out all museums from newest to oldest.
    If a search index is available, this page will also
    have the option to search through museums.
    """
    has_index = get_setting('site', 'global', 'searchindex')
    query = request.GET.get('q', None)

    if has_index and query:
        museums = Museum.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'museums.view_story')
        museums = Museum.objects.filter(filters).distinct()
        if request.user.is_authenticated():
            museums = museums.select_related()
    museums = museums.order_by('ordering', '-create_dt')

    EventLog.objects.log(**{
        'event_id' : 1140400,
        'event_data': '%s searched by %s' % ('Museum', request.user),
        'description': '%s searched' % 'Museum',
        'user': request.user,
        'request': request,
        'source': 'museums'
    })
    
    return render_to_response(template_name, {'museums':museums}, 
        context_instance=RequestContext(request))

def search_redirect(request):
    return HttpResponseRedirect(reverse('museums'))
