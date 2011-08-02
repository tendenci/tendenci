from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from S_P_LOW.models import S_S_CAP
from perms.utils import get_notice_recipients, has_perm
from event_logs.models import EventLog

from perms.utils import is_admin

try:
    from notification import models as notification
except:
    notification = None

def index(request, template_name="S_P_LOW/detail.html"):
    return HttpResponseRedirect(reverse('S_P_LOW.search'))

def detail(request, pk=None, template_name="S_P_LOW/detail.html"):
    if not pk: return HttpResponseRedirect(reverse('S_P_LOW.search'))
    S_S_LOW = get_object_or_404(S_S_CAP, pk=pk)
    
    if has_perm(request.user, 'S_S_LOW.view_S_S_LOW', S_S_LOW):
        log_defaults = {
            'event_id' : EVID500,
            'event_data': '%s (%d) viewed by %s' % (S_S_LOW._meta.object_name, S_S_LOW.pk, request.user),
            'description': '%s viewed' % S_S_LOW._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': S_S_LOW,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'S_S_LOW': S_S_LOW}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="S_P_LOW/search.html"):
    query = request.GET.get('q', None)
    S_P_LOW = S_S_CAP.objects.search(query, user=request.user)
    S_P_LOW = S_P_LOW.order_by('-create_dt')

    log_defaults = {
        'event_id' : EVID400,
        'event_data': '%s searched by %s' % ('S_S_CAP', request.user),
        'description': '%s searched' % 'S_S_CAP',
        'user': request.user,
        'request': request,
        'source': 'S_P_LOW'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'S_P_LOW':S_P_LOW}, 
        context_instance=RequestContext(request))