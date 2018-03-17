import subprocess

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from django.utils.translation import ugettext as _

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.libs.utils import python_executable
from tendenci.apps.base.http import Http403
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
            subprocess.Popen([python_executable(), 'manage.py', 'celeryd_detach'])

            return redirect("export_detail", result.task_id)
    else:
        form = form_class()

    return render_to_resp(request=request, template_name=template_name,context={
        'form':form,
    })

@login_required
def detail(request, task_id, template_name="wp_exporter/detail.html"):
    #try:
    #    task = TaskMeta.objects.get(task_id=task_id)
    #except TaskMeta.DoesNotExist:
    #    #tasks database entries are not created at once.
    #    #instead of raising 404 we'll assume that there will be one for
    #    #the id.
    #    task = None

    messages.add_message(
        request,
        messages.INFO,
        _("Your site export is being processed. You will receive an email at %s when the export is complete." % request.user.email)
    )

    return render_to_resp(request=request, template_name=template_name)

@login_required
def download(request, export_id):
    try:
        export = XMLExport.objects.get(pk=export_id, author=request.user)
    except XMLExport.DoesNotExist:
        raise Http403

    xml = export.xml
    response = HttpResponse(xml)
    response['Content-Disposition'] = 'attachment; filename="export.xml"'

    return response
