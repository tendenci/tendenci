# python
import os

# django
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson as json

# local 
from theme.utils import get_theme
from theme_editor.models import ThemeFileVersion
from theme_editor.forms import FileForm, ThemeSelectForm, UploadForm
from theme_editor.utils import get_dir_list, get_file_list, get_file_content
from theme_editor.utils import qstr_is_file, qstr_is_dir, copy
from theme_editor.utils import handle_uploaded_file

from base.http import Http403
from perms.utils import has_perm

DEFAULT_FILE = 'templates/homepage.html'

@permission_required('theme_editor.change_themefileversion')
def edit_file(request, form_class=FileForm, template_name="theme_editor/index.html"):

    # if no permission; raise 403 exception
    if not has_perm(request.user,'theme_editor.view_themefileversion'):
        raise Http403
        
    selected_theme = request.GET.get("theme_edit", get_theme())
    theme_root = os.path.join(settings.CUSTOM_TEMPLATES_DIR, selected_theme)
    
    # get the default file and clean up any input
    default_file = request.GET.get("file", DEFAULT_FILE)
    
    if default_file:
        default_file = default_file.replace('\\','/')
        default_file = default_file.strip('/')
        default_file = default_file.replace('////', '/')
        default_file = default_file.replace('///', '/')
        default_file = default_file.replace('//', '/')
    
    
    # if the default_file is not a directory or file within
    # the themes folder then return a 404
    if not qstr_is_file(default_file, ROOT_DIR=theme_root) and not qstr_is_dir(default_file, ROOT_DIR=theme_root):
        raise Http404("Custom template not found")
    
    # if default_file is a directory then append the
    # trailing slash so we can get the dirname below
    if qstr_is_dir(default_file, ROOT_DIR=theme_root):
        default_file = '%s/' % default_file
    
    # get the current file name
    current_file = os.path.basename(default_file)
    
    # get the present working directory
    # and make sure they cannot list root
    pwd = os.path.dirname(default_file)
    if pwd == '/':
        pwd = ''

    # get the previous directory name and path
    prev_dir = '/'
    prev_dir_name = 'theme base'
    pwd_split = pwd.split('/')
    if len(pwd_split) > 1:
        prev_dir_name = pwd_split[-2]
        pwd_split.pop()
        prev_dir = '/'.join(pwd_split)
    elif not pwd_split[0]:
        prev_dir = ''
    
    # get the direcory list
    dirs = get_dir_list(pwd, ROOT_DIR=theme_root)
    
    # get the file list
    files, non_editable_files = get_file_list(pwd, ROOT_DIR=theme_root)
    
    # get a list of revisions
    archives = ThemeFileVersion.objects.filter(relative_file_path=default_file).order_by("-create_dt")
    
    if request.method == "POST":
        file_form = form_class(request.POST)
        if file_form.is_valid():
            if file_form.save(request, default_file, ROOT_DIR=theme_root):
                message = "Successfully updated %s" % current_file
            else:
                message = "Cannot update"
            request.user.message_set.create(message=_(message))
    else:
        content = get_file_content(default_file,  ROOT_DIR=theme_root)
        file_form = form_class({"content":content, "rf_path":default_file})
    
    theme_form = ThemeSelectForm(initial = {'theme_edit':selected_theme})
    upload_form = UploadForm(initial = {'file_dir':pwd})
    
    return render_to_response(template_name, {'file_form': file_form,
                                              'theme_form': theme_form,
                                              'upload_form': upload_form,
                                              'current_theme':selected_theme,
                                              'current_file': current_file,
                                              'prev_dir_name': prev_dir_name,
                                              'prev_dir': prev_dir,
                                              'pwd':pwd,
                                              'dirs':dirs,
                                              'files': files,
                                              'non_editable_files': non_editable_files,
                                              'archives':archives},
                              context_instance=RequestContext(request))
 
@login_required
def get_version(request, id):
    version = ThemeFileVersion.objects.get(pk=id)
    return HttpResponse(version.content)
    

@permission_required('theme_editor.change_themefileversion')
def original_templates(request, template_name="theme_editor/original_templates.html"):
    
    current_dir = request.GET.get("dir", '')
    if current_dir:
        current_dir = current_dir.replace('\\','/')
        current_dir = current_dir.strip('/')
        current_dir = current_dir.replace('////', '/')
        current_dir = current_dir.replace('///', '/')
        current_dir = current_dir.replace('//', '/')

    # if current_dir is a directory then append the
    # trailing slash so we can get the dirname below
    
    # get the previous directory name and path
    prev_dir = '/'
    prev_dir_name = 'original templates'
    current_dir_split = current_dir.split('/')
    if len(current_dir_split) > 1:
        prev_dir_name = current_dir_split[-2]
        current_dir_split.pop()
        prev_dir = '/'.join(current_dir_split)
    elif not current_dir_split[0]:
        prev_dir = ''
    
    dirs = get_dir_list(current_dir, ROOT_DIR = os.path.join(settings.PROJECT_ROOT, "templates"), include_plugins=True)
    files, non_editable_files = get_file_list(current_dir, ROOT_DIR = os.path.join(settings.PROJECT_ROOT, "templates"), include_plugins=True)
    return render_to_response(template_name, {
                                                'current_dir': current_dir,
                                                'prev_dir_name': prev_dir_name,
                                                'prev_dir':prev_dir,
                                                'dirs': dirs,
                                                'files': files,
                                                'non_editable_files': non_editable_files},
                              context_instance=RequestContext(request))

@permission_required('theme_editor.change_themefileversion')
def copy_to_theme(request):
    
    current_dir = request.GET.get("dir", '')
    if current_dir:
        current_dir = current_dir.replace('\\','/')
        current_dir = current_dir.strip('/')
        current_dir = current_dir.replace('////', '/')
        current_dir = current_dir.replace('///', '/')
        current_dir = current_dir.replace('//', '/')
    
    plugin = None
    if current_dir.startswith('plugins.'):
        plugin = current_dir.split('plugins.')[1].split('/')[0]
        current_dir = current_dir.split('plugins.')[1]
    
    chosen_file = request.GET.get("file", '')
    if chosen_file:
        chosen_file = chosen_file.replace('\\','/')
        chosen_file = chosen_file.strip('/')
        chosen_file = chosen_file.replace('////', '/')
        chosen_file = chosen_file.replace('///', '/')
        chosen_file = chosen_file.replace('//', '/')
    
    if plugin:
        full_filename = os.path.join(settings.PROJECT_ROOT, "plugins",
            plugin, 'templates', current_dir,
            chosen_file)
    else:
        full_filename = os.path.join(settings.PROJECT_ROOT, 'templates',
            current_dir, chosen_file)
    
    if not os.path.isfile(full_filename):
        raise Http404
        
    copy(current_dir, chosen_file, plugin=plugin)
    
    messages.add_message(request, messages.INFO, ('Successfully copied %s/%s to the the theme root' % (current_dir, chosen_file)))
    
    return redirect('original_templates')


def delete_file(request):
    
    # if no permission; raise 403 exception
    if not has_perm(request.user,'theme_editor.change_themefileversion'):
        raise Http403
    
    current_dir = request.GET.get("dir", '')
    if current_dir:
        current_dir = current_dir.replace('\\','/')
        current_dir = current_dir.strip('/')
        current_dir = current_dir.replace('////', '/')
        current_dir = current_dir.replace('///', '/')
        current_dir = current_dir.replace('//', '/')
    
    plugin = None
    if current_dir.startswith('plugins.'):
        plugin = current_dir.split('plugins.')[1].split('/')[0]
        current_dir = current_dir.split('plugins.')[1]
    
    chosen_file = request.GET.get("file", '')
    if chosen_file:
        chosen_file = chosen_file.replace('\\','/')
        chosen_file = chosen_file.strip('/')
        chosen_file = chosen_file.replace('////', '/')
        chosen_file = chosen_file.replace('///', '/')
        chosen_file = chosen_file.replace('//', '/')
    
    full_filename = os.path.join(settings.PROJECT_ROOT, "themes",
        get_theme(), current_dir,
        chosen_file)
    
    if not os.path.isfile(full_filename):
        raise Http404
    
    os.remove(full_filename)
    
    messages.add_message(request, messages.INFO, ('Successfully deleted %s/%s.' % (current_dir, chosen_file)))
    
    return redirect('theme_editor')
    
def upload_file(request, template_name="theme_editor/upload.html"):
    # if no permission; raise 403 exception
    if not has_perm(request.user,'theme_editor.add_themefileversion'):
        raise Http403
    
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = request.FILES['upload']
            file_dir = form.cleaned_data['file_dir']
            overwrite = form.cleaned_data['overwrite']
            full_filename = os.path.join(settings.PROJECT_ROOT, "themes",
                get_theme(), file_dir, upload.name)
            
            if os.path.isfile(full_filename) and not overwrite:
                response = {
                    "error":"file already exists",
                    "file_name": os.path.join(file_dir, upload.name),
                }
                return HttpResponse(json.dumps(response), mimetype='application/json')
            else:
                handle_uploaded_file(upload)
                response = {
                    "success":True
                }
                messages.add_message(request, messages.INFO, ('Successfully uploaded %s.' % (upload.name)))
                return HttpResponse(json.dumps(response), mimetype='application/json')
    else:
        form = UploadForm()
        
    return render_to_response(template_name, {'form':form},
        context_instance=RequestContext(request))
