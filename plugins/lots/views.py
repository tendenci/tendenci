from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from lots.models import Lot
from perms.utils import get_notice_recipients, has_perm
from event_logs.models import EventLog

from perms.utils import is_admin

try:
    from notification import models as notification
except:
    notification = None

def index(request, template_name="lots/detail.html"):
    return HttpResponseRedirect(reverse('lots.search'))

def detail(request, pk=None, template_name="lots/detail.html"):
    if not pk: return HttpResponseRedirect(reverse('lots.search'))
    lot = get_object_or_404(Lot, pk=pk)
    
    if has_perm(request.user, 'lot.view_lot', lot):
        log_defaults = {
            'event_id' : 9999500,
            'event_data': '%s (%d) viewed by %s' % (lot._meta.object_name, lot.pk, request.user),
            'description': '%s viewed' % lot._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': lot,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'lot': lot}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="lots/search.html"):
    query = request.GET.get('q', None)
    lots = Lot.objects.search(query, user=request.user)
    lots = lots.order_by('-create_dt')

    log_defaults = {
        'event_id' : 9999400,
        'event_data': '%s searched by %s' % ('Lot', request.user),
        'description': '%s searched' % 'Lot',
        'user': request.user,
        'request': request,
        'source': 'lots'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'lots':lots}, 
        context_instance=RequestContext(request))