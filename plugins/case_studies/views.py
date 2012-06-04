from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse

from base.http import Http403
from perms.utils import has_perm, is_admin, has_view_perm, get_query_filters
from event_logs.models import EventLog
from site_settings.utils import get_setting

from models import CaseStudy, Service, Technology

def index(request, slug=None, template_name="case_studies/view.html"):
    if not slug: return HttpResponseRedirect(reverse('case_study'))
    case_study = get_object_or_404(CaseStudy, slug=slug)
    services = Service.objects.all()
    technologies = Technology.objects.all()

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (case_study.status_detail).lower() <> 'active' and (not is_admin(request.user)):
        raise Http403

    if has_view_perm(request.user, 'case_studies.view_casestudy', case_study):
        log_defaults = {
            'event_id' : 1000500,
            'event_data': '%s (%d) viewed by %s' % (case_study._meta.object_name, case_study.pk, request.user),
            'description': '%s viewed' % case_study._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': case_study,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'case_study': case_study, 'services': services, 'technologies': technologies},
            context_instance=RequestContext(request))
    else:
        raise Http403


def search(request, template_name="case_studies/search.html"):
    query = request.GET.get('q', None)

    if get_setting('site', 'global', 'searchindex') and query:
        case_studies = CaseStudy.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'case_studies.view_casestudy')
        case_studies = CaseStudy.objects.filter(filters).distinct()
        if not request.user.is_anonymous():
            case_studies = case_studies.select_related()
    case_studies = case_studies.order_by('-create_dt')
    services = Service.objects.all()
    technologies = Technology.objects.all()
    
    log_defaults = {
        'event_id' : 1000400,
        'event_data': '%s searched by %s' % ('Case Study', request.user),
        'description': '%s searched' % 'Case Study',
        'user': request.user,
        'request': request,
        'source': 'case_studies'
    }
    EventLog.objects.log(**log_defaults)

    return render_to_response(template_name, {'case_studies': case_studies, 'services': services, 'technologies': technologies},
        context_instance=RequestContext(request))


def search_redirect(request):
    return HttpResponseRedirect(reverse('case_study'))


def service(request, id, template_name="case_studies/search.html"):
    "List of case studies by service"
    service = get_object_or_404(Service, pk=id)
    query = '"service:%s"' % service
    services = Service.objects.all()

    case_studies = CaseStudy.objects.search(query, user=request.user)

    return render_to_response(template_name, {'service':service, 'services':services, 'case_studies': case_studies}, 
        context_instance=RequestContext(request))
        
def technology(request, id, template_name="case_studies/search.html"):
    "List of case studies by technology"
    technology = get_object_or_404(Technology, pk=id)
    query = '"technology:%s"' % technology

    case_studies = CaseStudy.objects.search(query, user=request.user)

    return render_to_response(template_name, {'technology':technology, 'case_studies': case_studies}, 
        context_instance=RequestContext(request))