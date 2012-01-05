from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from museums.models import Museum
from perms.utils import get_notice_recipients, has_perm
from event_logs.models import EventLog

from perms.utils import is_admin

try:
    from notification import models as notification
except:
    notification = None

def index(request, template_name="museums/detail.html"):
    return HttpResponseRedirect(reverse('museums.search'))

def detail(request, pk=None, template_name="museums/detail.html"):
    if not pk: return HttpResponseRedirect(reverse('museums.search'))
    museum = get_object_or_404(Museum, pk=pk)
    
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
    query = request.GET.get('q', None)
    museums = Museum.objects.search(query, user=request.user)
    museums = museums.order_by('-create_dt')

    log_defaults = {
        'event_id' : 1140400,
        'event_data': '%s searched by %s' % ('Museum', request.user),
        'description': '%s searched' % 'Museum',
        'user': request.user,
        'request': request,
        'source': 'museums'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'museums':museums}, 
        context_instance=RequestContext(request))