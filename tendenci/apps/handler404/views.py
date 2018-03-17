from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.perms.decorators import superuser_required
from tendenci.apps.handler404.models import Report404
from tendenci.apps.event_logs.models import EventLog


@superuser_required
def reports_404(request, template_name='reports/404_report.html'):
    entry_list = Report404.objects.all().order_by('-count')

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={
        'entry_list': entry_list,
    })
