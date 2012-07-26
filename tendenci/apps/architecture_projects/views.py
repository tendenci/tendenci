from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse

from tendenci.core.base.http import Http403
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.utils import has_perm, get_query_filters, has_view_perm
from tendenci.core.event_logs.models import EventLog

from tendenci.apps.architecture_projects.models import ArchitectureProject, Category, BuildingType

def detail(request, slug=None, template_name="architecture_projects/view.html"):
    if not slug: return HttpResponseRedirect(reverse('architecture_project.search'))
    architecture_project = get_object_or_404(ArchitectureProject, slug=slug)
    categories = Category.objects.all()
    building_types = BuildingType.objects.all()

    if has_view_perm(request.user, 'architecture_projects.view_architectureproject', architecture_project):
        EventLog.objects.log(instance=architecture_project)

        return render_to_response(template_name, {'architecture_project': architecture_project, 'categories': categories, 'building_types': building_types},
            context_instance=RequestContext(request))
    else:
        raise Http403


def search(request, template_name="architecture_projects/search.html"):
    query = request.GET.get('q', None)
    
    if get_setting('site', 'global', 'searchindex') and query:
        architecture_projects = ArchitectureProject.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'architecture_projects.view_architectureproject')
        architecture_projects = ArchitectureProject.objects.filter(filters)

    architecture_projects = architecture_projects.order_by('-ordering')
    categories = Category.objects.all()
    building_types = BuildingType.objects.all()

    EventLog.objects.log()

    return render_to_response(template_name, {'architecture_projects': architecture_projects, 'categories': categories, 'building_types': building_types},
        context_instance=RequestContext(request))


def category(request, id, template_name="architecture_projects/search.html"):
    "List of architecture projects by category"
    category = get_object_or_404(Category, pk=id)
    filters = get_query_filters(request.user, 'architecture_projects.view_architectureproject')
    architecture_projects = ArchitectureProject.objects.filter(filters).filter(categories=category).order_by('-ordering')

    categories = Category.objects.all()
    building_types = BuildingType.objects.all()

    EventLog.objects.log()

    return render_to_response(template_name, {'category':category, 'architecture_projects': architecture_projects, 'categories': categories, 'building_types': building_types}, 
        context_instance=RequestContext(request))


def building_type(request, id, template_name="architecture_projects/search.html"):
    "List of architecture projects by building_type"
    building_type = get_object_or_404(BuildingType, pk=id)
    filters = get_query_filters(request.user, 'architecture_projects.view_architectureproject')
    architecture_projects = ArchitectureProject.objects.filter(filters).filter(building_types=building_type).order_by('-ordering')

    categories = Category.objects.all()
    building_types = BuildingType.objects.all()

    EventLog.objects.log()

    return render_to_response(template_name, {'building_type':building_type, 'architecture_projects': architecture_projects, 'categories': categories, 'building_types': building_types}, 
        context_instance=RequestContext(request))
