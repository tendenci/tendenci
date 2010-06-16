# python
import os

# django
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext_lazy as _

# local 
from theme_editor.models import ThemeFileVersion
from theme_editor.forms import FileForm
from theme_editor.utils import get_file_attr, get_files_list, get_file_content

from base.http import Http403

DEFAULT_FILE = 'templates/nav.html'

@permission_required('theme_editor.change_themefileversion')
def edit_file(request, form_class=FileForm, template_name="theme_editor/index.html"):

    # if no permission; raise 404 exception
    if not request.user.has_perm('theme_editor.view_themefileversion'):
        raise Http403  

    file_relative_path = request.GET.get("file", DEFAULT_FILE)
    if file_relative_path:
        file_relative_path = file_relative_path.replace("\\", "/")
        if file_relative_path[0] == "/":
            file_relative_path = file_relative_path[1:]
        
    file_path = (os.path.join(settings.THEME_ROOT, file_relative_path)).replace("\\", "/")
    file_dict = get_file_attr(file_path)
    files_list = get_files_list(settings.THEME_ROOT)
    
    # get a list of revisions
    archives = ThemeFileVersion.objects.filter(relative_file_path=file_relative_path).order_by("-create_dt")
    
    if request.method == "POST":
        file_form = form_class(request.POST)
        if file_form.is_valid():
            if file_form.save(request, file_relative_path):
                message = "Successfully updated"
            else:
                message = "Cannot update"
            request.user.message_set.create(message=_(message + " %s '%s'") % (file_dict["type"].lower(), file_dict["name"]))
    else:
        content = get_file_content(file_path)
        file_form = form_class({"content":content, "rf_path":file_relative_path})
    return render_to_response(template_name, {"file_form": file_form, 
                                              "file_dict":file_dict, 
                                              "files_list":files_list,
                                              "archives":archives}, 
                              context_instance=RequestContext(request))
 
@login_required
def get_version(request, id):
    version = ThemeFileVersion.objects.get(pk=id)
    return HttpResponse(version.content)