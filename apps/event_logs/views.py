from django.contrib.auth.decorators import permission_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import render_to_403
from event_logs.models import EventLog

@permission_required('event_logs.view_eventlog')
def index(request, id=None, template_name="event_logs/view.html"):
    if not id: return HttpResponseRedirect(reverse('event_log.search'))
    event_log = get_object_or_404(EventLog, pk=id)

    if request.user.has_perm('event_logs.view_eventlog', event_log):
        return render_to_response(template_name, {'event_log': event_log}, 
            context_instance=RequestContext(request))
    else:
        return render_to_403()

@permission_required('event_logs.view_eventlog')
def search(request, template_name="event_logs/search.html"):
    print "here"
    if request.method == 'GET':
        if 'q' in request.GET:
            query = request.GET['q']
        else:
            query = None
        event_logs = EventLog.objects.search(query)
    else:
        event_logs = EventLog.objects.search()
        
    return render_to_response(template_name, {'event_logs':event_logs}, 
        context_instance=RequestContext(request))

@permission_required('event_logs.view_eventlog')
def print_view(request, id, template_name="event_logs/print-view.html"):
    event_log = get_object_or_404(EventLog, pk=id)
     
    if request.user.has_perm('articles.view_article', event_log):
        return render_to_response(template_name, {'event_log': event_log}, 
            context_instance=RequestContext(request))
    else:
        return render_to_403()