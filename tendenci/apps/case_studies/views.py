from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.perms.utils import has_perm, has_view_perm, get_query_filters
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.case_studies.models import CaseStudy, Service, Technology


def detail(request, slug=None, template_name="case_studies/view.html"):
    if not slug: return HttpResponseRedirect(reverse('case_study'))
    case_study = get_object_or_404(CaseStudy, slug=slug)
    services = Service.objects.all()
    technologies = Technology.objects.all()

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (case_study.status_detail).lower() != 'active' and (not request.user.profile.is_superuser):
        raise Http403

    if has_view_perm(request.user, 'case_studies.view_casestudy', case_study):
        EventLog.objects.log(instance=case_study)

        return render_to_resp(request=request, template_name=template_name,
            context={'case_study': case_study, 'services': services, 'technologies': technologies})
    else:
        raise Http403


def search(request, template_name="case_studies/search.html"):
    query = request.GET.get('q', None)

    if get_setting('site', 'global', 'searchindex') and query:
        case_studies = CaseStudy.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'case_studies.view_casestudy')
        case_studies = CaseStudy.objects.filter(filters).distinct()
        if not request.user.is_anonymous:
            case_studies = case_studies.select_related()
    case_studies = case_studies.order_by('-create_dt')
    services = Service.objects.all()
    technologies = Technology.objects.all()

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'case_studies': case_studies, 'services': services, 'technologies': technologies})


def search_redirect(request):
    return HttpResponseRedirect(reverse('case_study'))


def service(request, id, template_name="case_studies/search.html"):
    "List of case studies by service"
    service = get_object_or_404(Service, pk=id)
    query = '"service:%s"' % service
    services = Service.objects.all()

    case_studies = CaseStudy.objects.search(query, user=request.user)

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'service':service, 'services':services, 'case_studies': case_studies})

def technology(request, id, template_name="case_studies/search.html"):
    "List of case studies by technology"
    technology = get_object_or_404(Technology, pk=id)
    query = '"technology:%s"' % technology

    case_studies = CaseStudy.objects.search(query, user=request.user)

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'technology':technology, 'case_studies': case_studies})

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'technology':technology, 'case_studies': case_studies})

def print_view(request, id, template_name="case_studies/print-view.html"):
    case_study = get_object_or_404(CaseStudy, id=id)
    services = Service.objects.all()
    technologies = Technology.objects.all()

    if (case_study.status_detail).lower() != 'active' and (not request.user.profile.is_superuser):
        raise Http403

    if not has_perm(request.user, 'case_studies.view_casestudy', case_study):
        raise Http403

    EventLog.objects.log(instance=case_study)

    return render_to_resp(request=request, template_name=template_name,
        context={'case_study': case_study, 'services': services, 'technologies': technologies})
