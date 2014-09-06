import subprocess
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.template import Template
from djcelery.models import TaskMeta

from tendenci.apps.base.http import Http403
from tendenci.apps.perms.utils import has_perm
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.wp_exporter.utils import gen_xml
from tendenci.apps.wp_exporter.forms import ExportForm
from tendenci.apps.wp_exporter.tasks import WPExportTask
from tendenci.apps.wp_exporter.models import XMLExport

def index(request, form_class=ExportForm ,template_name="wp_exporter/index.html"):
    if not request.user.profile.is_superuser:
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            result = WPExportTask.delay(form, request.user)
            #uncomment the next line if there is no celery server yet.
            #result.wait()
            subprocess.Popen(['python', 'manage.py', 'celeryd_detach'])

            return redirect("export_detail", result.task_id)
    else:
        form = form_class()

    return render_to_response(template_name, {
        'form':form,
    },context_instance=RequestContext(request))

@login_required
def detail(request, task_id, template_name="wp_exporter/detail.html"):
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        #tasks database entries are not created at once.
        #instead of raising 404 we'll assume that there will be one for
        #the id.
        task = None

    messages.add_message(
        request,
        messages.INFO,
        _("Your site export is being processed. You will receive an email at %s when the export is complete." % request.user.email)
    )

    return render_to_response(template_name, {},
        context_instance=RequestContext(request))

@login_required
def download(request, export_id):
    try:
        export = XMLExport.objects.get(pk=export_id, author=request.user)
    except XMLExport.DoesNotExist:
        raise Http403

    xml = export.xml
    response = HttpResponse(xml)
    response['Content-Disposition'] = 'attachment; filename=export.xml'

    return response
