from datetime import datetime

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.exports.models import Export


@login_required
def status(request, export_id, template_name='exports/export_status.html'):
    """Checks if an export is completed.
    """

    if not request.user.is_superuser:
        raise Http403

    #invalidate('exports_export')
    export = get_object_or_404(Export, pk=export_id)

    return render_to_resp(request=request, template_name=template_name, context={
        'export': export,
        'datetime': datetime,
    })


@login_required
def download(request, export_id):
    """Returns the export file if it exists"""

    if not request.user.is_superuser:
        raise Http403

    export = get_object_or_404(Export, pk=export_id)

    EventLog.objects.log(instance=export)

    if export.status == "completed":
        response = export.result
        return response

    return redirect("export.status", export_id)
