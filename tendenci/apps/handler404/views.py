from django.template import RequestContext
from django.shortcuts import render_to_response

from tendenci.apps.perms.decorators import superuser_required
from tendenci.apps.handler404.models import Report404
from tendenci.apps.event_logs.models import EventLog


@superuser_required
def reports_404(request, template_name='reports/404_report.html'):
    entry_list = Report404.objects.all().order_by('-count')

    EventLog.objects.log()

    return render_to_response(template_name, {
        'entry_list': entry_list,
    }, context_instance=RequestContext(request))
