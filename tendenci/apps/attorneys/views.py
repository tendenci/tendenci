from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404

from tendenci.core.base.http import Http403
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.utils import has_perm, get_query_filters
from tendenci.core.event_logs.models import EventLog
from tendenci.apps.attorneys.models import Attorney
from tendenci.apps.attorneys.utils import get_vcard_content

def index(request, template_name='attorneys/index.html'):
    if get_setting('site', 'global', 'searchindex'):
        attorneys = Attorney.objects.search(query=None, user=request.user)
    else:
        filters = get_query_filters(request.user, 'attorneys.view_attorney')
        attorneys = Attorney.objects.filter(filters).distinct()
    attorneys = attorneys.order_by('ordering','create_dt')

    EventLog.objects.log()

    return render_to_response(template_name,
        {
            'attorneys':attorneys,
        },
        context_instance=RequestContext(request))
    
def search(request, template_name='attorneys/search.html'):
    category = request.GET.get('category', None)
    q = request.GET.get('q', None)
    
    if get_setting('site', 'global', 'searchindex') and q:
        attorneys = Attorney.objects.search(query=q, user=request.user)
        
    else:
        filters = get_query_filters(request.user, 'attorneys.view_attorney')
        attorneys = Attorney.objects.filter(filters).distinct()
        if request.user.is_authenticated():
            attorneys = attorneys.select_related()
    
    attorneys = attorneys.order_by('ordering','create_dt')
    
    if category:
        attorneys = attorneys.filter(category=category)

    EventLog.objects.log()

    return render_to_response(template_name, 
        {
            'attorneys':attorneys,
        },
        context_instance=RequestContext(request))

def detail(request, slug=None, template_name='attorneys/detail.html'):
    attorney = get_object_or_404(Attorney, slug=slug)
    
    if not has_perm(request.user, 'attorneys.view_attorney', attorney):
        raise Http403

    EventLog.objects.log(instance=attorney)

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
    EventLog.objects.log(instance=attorney)
    filename = "%s.vcf" % (attorney.slug)
    response = HttpResponse(output, mimetype="text/x-vCard")
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
