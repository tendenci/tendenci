
import subprocess
from wsgiref.util import FileWrapper

from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.base import View

from explorer import app_settings
from explorer.views import PermissionRequiredMixin

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.libs.utils import python_executable
from tendenci.apps.base.http import Http403
from tendenci.apps.explorer_extensions.models import DatabaseDumpFile
from tendenci.apps.explorer_extensions.forms import DatabaseDumpForm


def get_app_permissions(request):
    return {'can_view': app_settings.EXPLORER_PERMISSION_VIEW(request.user),
            'can_change': app_settings.EXPLORER_PERMISSION_CHANGE(request.user)}

def _export_page(request):
    ctx = {}
    ctx.update(get_app_permissions(request))

    form = None
    if request.method == 'POST':
        form = DatabaseDumpForm(request.POST)
        if form.is_valid():
            print("Form submitted is valid!")
            if can_create_dump():
                new_obj = DatabaseDumpFile()
                new_obj.author = request.user
                new_obj.export_format = form.cleaned_data['format']
                new_obj.save()
                subprocess.Popen([python_executable(), "manage.py",
                              "create_database_dump",
                              str(request.user.pk), form.cleaned_data['format'], str(new_obj.pk) ])
                messages.add_message(request, messages.INFO, "Success! The system is now generating your export file. Please reload in a few seconds to update the list.")
            else:
                messages.add_message(request, messages.ERROR, "Cannot create file. You have already reached the limit of existing dump files. Please delete old unused exports and try again.")
    else:
        form = DatabaseDumpForm()

    # get all active DB Dump Files
    # if current existing DB Dump Files are less than the limit, enable form submission
    db_objs = DatabaseDumpFile.objects.filter(~Q(status='expired'))

    ctx['objects'] = db_objs
    if can_create_dump():
        ctx['enable_form'] = True

    ctx['form'] = form
    return render_to_resp(request=request, template_name="explorer/export_page.html", context=ctx)
class _ExportPage(PermissionRequiredMixin, View):
    permission_required = 'change_permission'

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request, *args, **kwargs):
            return self.handle_no_permission(request)
        return _export_page(request)
export_page = _ExportPage.as_view()


@login_required
def download_dump(request, dump_id):
    dbdump = get_object_or_404(DatabaseDumpFile, pk=dump_id)
    if request.user != dbdump.author and not request.user.is_superuser:
        raise Http403
    if not dbdump.dbfile:
        raise Http404
    wrapper = FileWrapper(dbdump.dbfile)
    response = HttpResponse(wrapper, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="db_export.%s"' % dbdump.export_format
    return response


def delete_dump(request, dump_id):
    dbdump = get_object_or_404(DatabaseDumpFile, pk=dump_id)
    if request.user != dbdump.author and not request.user.is_superuser:
        raise Http403
    dbdump.delete()
    messages.add_message(request, messages.INFO, "Successfully deleted export file.")
    return redirect('explorer_extensions.export_page')


def can_create_dump():
    db_objs = DatabaseDumpFile.objects.filter(~Q(status='expired'))
    return db_objs.count() < 3
