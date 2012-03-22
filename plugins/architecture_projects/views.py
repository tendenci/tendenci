from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse

from base.http import Http403
from perms.utils import has_perm
from perms.utils import is_admin
from event_logs.models import EventLog

from models import ArchitectureProject, Category, BuildingType

def index(request, slug=None, template_name="architecture_projects/view.html"):
    if not slug: return HttpResponseRedirect(reverse('architecture_project.search'))
    architecture_project = get_object_or_404(ArchitectureProject, slug=slug)
    categories = Category.objects.all()
    building_types = BuildingType.objects.all()

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (architecture_project.status_detail).lower() <> 'active' and (not is_admin(request.user)):
        raise Http403

    if has_perm(request.user, 'architecture_projects.view_architectureproject', architecture_project):
        log_defaults = {
            'event_id' : 1000500,
            'event_data': '%s (%d) viewed by %s' % (architecture_project._meta.object_name, architecture_project.pk, request.user),
            'description': '%s viewed' % architecture_project._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': architecture_project,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'architecture_project': architecture_project, 'categories': categories, 'building_types': building_types},
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="architecture_projects/search.html"):
    query = request.GET.get('q', None)
    architecture_projects = ArchitectureProject.objects.search(query, user=request.user)
    architecture_projects = architecture_projects.order_by('-create_dt')
    categories = Category.objects.all()
    building_types = BuildingType.objects.all()
    
    log_defaults = {
        'event_id' : 1000400,
        'event_data': '%s searched by %s' % ('Architecture Project', request.user),
        'description': '%s searched' % 'Architecture Project',
        'user': request.user,
        'request': request,
        'source': 'architecture_projects'
    }
    EventLog.objects.log(**log_defaults)

    return render_to_response(template_name, {'architecture_projects': architecture_projects, 'categories': categories, 'building_types': building_types},
        context_instance=RequestContext(request))        
def category(request, id, template_name="architecture_projects/search.html"):
    "List of architecture projects by category"
    category = get_object_or_404(Category, pk=id)
    query = '"category:%s"' % category

    architecture_projects = ArchitectureProject.objects.search(query, user=request.user)

    return render_to_response(template_name, {'category':category, 'architecture_projects': architecture_projects}, 
        context_instance=RequestContext(request))
        
def building_type(request, id, template_name="architecture_projects/search.html"):
    "List of architecture projects by building_type"
    building_type = get_object_or_404(BuildingType, pk=id)
    query = '"building_type:%s"' % building_type

    architecture_projects = ArchitectureProject.objects.search(query, user=request.user)

    return render_to_response(template_name, {'building_type':building_type, 'architecture_projects': architecture_projects}, 
        context_instance=RequestContext(request))