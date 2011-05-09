from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from quotes.models import Quote
from perms.object_perms import ObjectPermission
from perms.utils import get_notice_recipients, has_perm
from event_logs.models import EventLog

from perms.utils import is_admin

try:
    from notification import models as notification
except:
    notification = None

def index(request, pk=None, template_name="quotes/view.html"):
    if not pk: return HttpResponseRedirect(reverse('quote.search'))
    quote = get_object_or_404(Quote, pk=pk)
    
    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (quote.status_detail).lower() <> 'active' and (not is_admin(request.user)):
        raise Http403
    
    if has_perm(request.user, 'quotes.view_quote', quote):
        log_defaults = {
            'event_id' : 435000,
            'event_data': '%s (%d) viewed by %s' % (quote._meta.object_name, quote.pk, request.user),
            'description': '%s viewed' % quote._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': quote,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'quote': quote}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="quotes/search.html"):
    query = request.GET.get('q', None)
    quotes = Quote.objects.search(query, user=request.user)
    quotes = quotes.order_by('-create_dt')

    log_defaults = {
        'event_id' : 434000,
        'event_data': '%s searched by %s' % ('Quote', request.user),
        'description': '%s searched' % 'Quote',
        'user': request.user,
        'request': request,
        'source': 'quotes'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'quotes':quotes}, 
        context_instance=RequestContext(request))