from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from plugs.models import Plug
from perms.utils import get_notice_recipients, has_perm
from event_logs.models import EventLog

from perms.utils import is_admin

try:
    from notification import models as notification
except:
    notification = None

def index(request, template_name="plugs/detail.html"):
    return HttpResponseRedirect(reverse('plugs.search'))

def detail(request, pk=None, template_name="plugs/detail.html"):
    if not pk: return HttpResponseRedirect(reverse('plugs.search'))
    plug = get_object_or_404(Plug, pk=pk)
    
    if has_perm(request.user, 'plug.view_plug', plug):
        log_defaults = {
            'event_id' : 100500,
            'event_data': '%s (%d) viewed by %s' % (plug._meta.object_name, plug.pk, request.user),
            'description': '%s viewed' % plug._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': plug,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'plug': plug}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="plugs/search.html"):
    query = request.GET.get('q', None)
    plugs = Plug.objects.search(query, user=request.user)
    plugs = plugs.order_by('-create_dt')

    log_defaults = {
        'event_id' : 100400,
        'event_data': '%s searched by %s' % ('Plug', request.user),
        'description': '%s searched' % 'Plug',
        'user': request.user,
        'request': request,
        'source': 'plugs'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'plugs':plugs}, 
        context_instance=RequestContext(request))