from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from projects.models import Project
from perms.utils import get_notice_recipients, has_perm
from event_logs.models import EventLog

try:
    from notification import models as notification
except:
    notification = None

def index(request, template_name="projects/detail.html"):
    return HttpResponseRedirect(reverse('projects.search'))

def detail(request, slug=None, template_name="projects/detail.html"):
    if not slug: return HttpResponseRedirect(reverse('projects.search'))
    project = get_object_or_404(Project, slug=slug)
    
    if has_perm(request.user, 'project.view_project', project):
        log_defaults = {
            'event_id' : 1180500,
            'event_data': '%s (%d) viewed by %s' % (project._meta.object_name, project.pk, request.user),
            'description': '%s viewed' % project._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': project,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'project': project}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="projects/search.html"):
    query = request.GET.get('q', None)
    projects = Project.objects.search(query, user=request.user)
    projects = projects.order_by('-create_dt')

    log_defaults = {
        'event_id' : 1180400,
        'event_data': '%s searched by %s' % ('Project', request.user),
        'description': '%s searched' % 'Project',
        'user': request.user,
        'request': request,
        'source': 'projects'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'projects':projects}, 
        context_instance=RequestContext(request))
