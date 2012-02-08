from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404

from base.http import Http403
from site_settings.utils import get_setting
from perms.utils import has_perm
from event_logs.models import EventLog
from attorneys.models import Attorney
from attorneys.utils import get_vcard_content

def index(request, template_name='attorneys/index.html'):
    attorneys = Attorney.objects.search(query=None, user=request.user)
    attorneys = attorneys.order_by('ordering','create_dt')
    
    log_defaults = {
        'event_id' : 496000,
        'event_data': '%s page viewed by %s' % ('Attorneys', request.user),
        'description': '%s viewed' % 'Attorneys',
        'user': request.user,
        'request': request,
        'source': 'attorneys'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, 
        {
            'attorneys':attorneys,
        },
        context_instance=RequestContext(request))

def search(request, template_name='attorneys/search.html'):
    category = request.GET.get('category', None)
    q = request.GET.get('q', None)
    
    attorneys = Attorney.objects.search(query=q, user=request.user)
    attorneys = attorneys.order_by('ordering','create_dt')
    
    if category:
        attorneys = attorneys.filter(category=category)
    
    log_defaults = {
        'event_id' : 494000,
        'event_data': '%s searched by %s' % ('Attorneys', request.user),
        'description': '%s searched' % 'Attorneys',
        'user': request.user,
        'request': request,
        'source': 'attorneys'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, 
        {
            'attorneys':attorneys,
        },
        context_instance=RequestContext(request))

def detail(request, slug=None, template_name='attorneys/detail.html'):
    attorney = get_object_or_404(Attorney, slug=slug)
    
    if not has_perm(request.user, 'attorneys.view_attorney', attorney):
        raise Http403
        
    log_defaults = {
        'event_id' : 495000,
        'event_data': '%s (%d) viewed by %s' % (attorney._meta.object_name, attorney.pk, request.user),
        'description': '%s viewed' % attorney._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': attorney,
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name,
        {
            'attorney': attorney,
        },
        context_instance=RequestContext(request))

def vcard(request, slug):
    """
    Method for returning single downloadable vcard
    """
    attorney = get_object_or_404(Attorney, slug=slug)
    output = get_vcard_content(attorney)
    filename = "%s.vcf" % (attorney.slug)
    response = HttpResponse(output, mimetype="text/x-vCard")
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
