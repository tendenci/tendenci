from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from rfps.models import RFP
from perms.utils import get_notice_recipients, has_perm
from event_logs.models import EventLog

try:
    from notification import models as notification
except:
    notification = None

def index(request, template_name="rfps/detail.html"):
    return HttpResponseRedirect(reverse('rfps.search'))

def detail(request, slug=None, template_name="rfps/detail.html"):
    if not slug: return HttpResponseRedirect(reverse('rfps.search'))
    rfp = get_object_or_404(RFP, slug=slug)
    
    if has_perm(request.user, 'rfp.view_rfp', rfp):
        log_defaults = {
            'event_id' : 1160500,
            'event_data': '%s (%d) viewed by %s' % (rfp._meta.object_name, rfp.pk, request.user),
            'description': '%s viewed' % rfp._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': rfp,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'rfp': rfp}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="rfps/search.html"):
    query = request.GET.get('q', None)
    rfps = RFP.objects.search(query, user=request.user)
    rfps = rfps.order_by('-create_dt')

    log_defaults = {
        'event_id' : 1160400,
        'event_data': '%s searched by %s' % ('RFP', request.user),
        'description': '%s searched' % 'RFP',
        'user': request.user,
        'request': request,
        'source': 'rfps'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'rfps':rfps}, 
        context_instance=RequestContext(request))
        
def search_redirect(request):
    return HttpResponseRedirect(reverse('rfps'))
