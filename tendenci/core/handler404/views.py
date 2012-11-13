from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponseNotFound

from tendenci.core.handler404.models import Report404
from tendenci.core.event_logs.models import EventLog

def handle_404(request, template_name='404.html'):
    try:
        report = Report404.objects.get(url=request.path)
        report.count = report.count + 1
    except Report404.DoesNotExist:
        report = Report404(url=request.path)
    report.save()

    EventLog.objects.log()
    t = loader.get_template(template_name)
    return HttpResponseNotFound(t.render(RequestContext(request,{'request_path': request.path})))

@staff_member_required 
def reports_404(request, template_name='reports/404_report.html'):
    entry_list = Report404.objects.all().order_by('-count')

    EventLog.objects.log()

    return render_to_response(template_name, {
        'entry_list':entry_list,
    }, context_instance=RequestContext(request))
