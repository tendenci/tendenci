from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from chamberlin_projects.models import Project, ConstructionCategory
from site_settings.utils import get_setting
from perms.utils import get_notice_recipients, get_query_filters, has_view_perm
from event_logs.models import EventLog

try:
    from tendenci.contrib.notifications import models as notification
except:
    notification = None

def index(request, template_name="chamberlin_projects/index.html"):
    categories = ConstructionCategory.objects.all().order_by('name')

    return render_to_response(template_name, {'categories':categories},
        context_instance=RequestContext(request))

def detail(request, category=None, slug=None, template_name="chamberlin_projects/detail.html"):
    if not slug: return HttpResponseRedirect(reverse('chamberlin_projects.search'))
    project = get_object_or_404(Project, slug=slug)
    if category != project.category:
        HttpResponseRedirect(reverse('chamberlin_projects.detail', args=[project.category, project.slug]))

    if has_view_perm(request.user, 'project.view_project', project):
        EventLog.objects.log(instance=project)
        return render_to_response(template_name, {'project': project}, 
            context_instance=RequestContext(request))
    else:
        raise Http403


def search(request, template_name="chamberlin_projects/search.html"):
    query = request.GET.get('q', None)
    if get_setting('site', 'global', 'searchindex') and query:
        chamberlin_projects = Project.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'chamberlin_projects.view_project')
        chamberlin_projects = Project.objects.filter(filters).distinct()

    chamberlin_projects = chamberlin_projects.order_by('-create_dt')

    EventLog.objects.log()

    return render_to_response(template_name, {'chamberlin_projects':chamberlin_projects},
        context_instance=RequestContext(request))


def category(request, category=None, template_name="chamberlin_projects/category.html"):
    category = get_object_or_404(ConstructionCategory, name=category)

    filters = get_query_filters(request.user, 'chamberlin_projects.view_project')
    chamberlin_projects = Project.objects.filter(filters).filter(category=category).distinct()
    chamberlin_projects = chamberlin_projects.order_by('construction_type','-create_dt')

    EventLog.objects.log()

    return render_to_response(template_name, {'chamberlin_projects':chamberlin_projects, 'category': category},
        context_instance=RequestContext(request))
