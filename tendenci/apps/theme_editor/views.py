import os

from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
import simplejson as json
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.base.http import Http403
from tendenci.apps.base.managers import SubProcessManager
from tendenci.apps.base.models import UpdateTracker
from tendenci.apps.base.utils import get_template_list, checklist_update
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.site_settings.models import Setting
from tendenci.apps.perms.utils import has_perm
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.theme.utils import get_theme, theme_choices as theme_choice_list
from tendenci.libs.boto_s3.utils import delete_file_from_s3
from tendenci.apps.theme_editor.models import ThemeFileVersion
from tendenci.apps.theme_editor.forms import (FileForm,
                                              ThemeSelectForm,
                                              UploadForm,
                                              AddTemplateForm)
from tendenci.apps.theme_editor.utils import get_dir_list, get_file_list, get_file_content, get_all_files_list
from tendenci.apps.theme_editor.utils import qstr_is_file, qstr_is_dir, copy
from tendenci.apps.theme_editor.utils import handle_uploaded_file, app_templates, ThemeInfo
from tendenci.libs.boto_s3.utils import save_file_to_s3

DEFAULT_FILE = 'templates/homepage.html'


@permission_required('theme_editor.change_themefileversion')
def edit_file(request, form_class=FileForm, template_name="theme_editor/index.html"):

    if not has_perm(request.user, 'theme_editor.view_themefileversion'):
        raise Http403

    selected_theme = request.GET.get("theme_edit", get_theme())
    original_theme_root = os.path.join(settings.ORIGINAL_THEMES_DIR, selected_theme)
    if settings.USE_S3_THEME:
        theme_root = os.path.join(settings.THEME_S3_PATH, selected_theme)
    else:
        theme_root = os.path.join(settings.ORIGINAL_THEMES_DIR, selected_theme)

    # get the default file and clean up any input
    default_file = request.GET.get("file", DEFAULT_FILE)

    if default_file:
        default_file = default_file.replace('\\', '/')
        default_file = default_file.strip('/')
        default_file = default_file.replace('////', '/')
        default_file = default_file.replace('///', '/')
        default_file = default_file.replace('//', '/')

    is_file = qstr_is_file(default_file, ROOT_DIR=theme_root)
    is_dir = qstr_is_dir(default_file, ROOT_DIR=theme_root)

    if is_file:
        pass
    elif is_dir:
        # if default_file is a directory then append the
        # trailing slash so we can get the dirname below
        default_file = '%s/' % default_file
    else:
        # if the default_file is not a directory or file within
        # the themes folder then return a 404
        raise Http404(_("Custom template not found. Make sure you've copied over the themes to the THEME_DIR."))

    # get the current file name
    current_file = os.path.basename(default_file)

    # get file ext
    name = current_file.split('/')[-1]
    ext = name.split('.')[-1]
    stylesheets = ['css', 'less']

    # get the present working directory
    # and make sure they cannot list root
    pwd = os.path.dirname(default_file)
    if pwd == '/':
        pwd = ''

    current_file_path = os.path.join(pwd, current_file)

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

    all_files_folders = get_all_files_list(ROOT_DIR=theme_root)

    # non-deletable files
    non_deletable_files = ['homepage.html', 'default.html', 'footer.html', 'header.html', 'sidebar.html', 'nav.html', 'styles.less', 'styles.css']

    # get the number of themes in the themes directory on the site
    theme_choices = [ i for i in theme_choice_list()]
    theme_count = len(theme_choices)

    # get a list of revisions
    archives = ThemeFileVersion.objects.filter(relative_file_path=default_file).order_by("-create_dt")

    if request.is_ajax() and request.method == "POST":
        file_form = form_class(request.POST)
        response_status = 'FAIL'
        response_message = _('Cannot update file.')
        if file_form.is_valid():
            if file_form.save(request, default_file, ROOT_DIR=theme_root, ORIG_ROOT_DIR=original_theme_root):
                response_status = 'SUCCESS'
                response_message = unicode(_('Your changes have been saved.'))
                EventLog.objects.log()

        response = json.dumps({'status':response_status, 'message':response_message})
        return HttpResponse(response, content_type="application/json")

    content = get_file_content(default_file,  ROOT_DIR=theme_root)
    file_form = form_class({"content": content, "rf_path": default_file})

    theme_form = ThemeSelectForm(initial={'theme_edit': selected_theme})

    return render_to_response(template_name, {
        'file_form': file_form,
        'theme_form': theme_form,
        'current_theme': selected_theme,
        'current_file_path': current_file_path,
        'current_file': current_file,
        'prev_dir_name': prev_dir_name,
        'prev_dir': prev_dir,
        'pwd': pwd,
        'dirs': dirs,
        'files': files,
        'non_editable_files': non_editable_files,
        'non_deletable_files': non_deletable_files,
        'theme_count': theme_count,
        'archives': archives,
        'is_file': is_file,
        'is_dir': is_dir,
        'all_files_folders': all_files_folders,
        'ext' : ext,
        'stylesheets' : stylesheets
    }, context_instance=RequestContext(request))


@permission_required('theme_editor.change_themefileversion')
@csrf_exempt
def create_new_template(request, form_class=AddTemplateForm):
    """
    Create a new blank template for a given template name
    """
    form = form_class(request.POST or None)
    ret_dict = {'created': False, 'err': ''}

    if form.is_valid():
        template_name = form.cleaned_data['template_name'].strip()
        template_full_name = 'default-%s.html' % template_name
        existing_templates = [t[0] for t in get_template_list()]
        if not template_full_name in existing_templates:
            # create a new template and assign default content
            use_s3_storage = getattr(settings, 'USE_S3_STORAGE', '')
            if use_s3_storage:
                theme_dir = settings.ORIGINAL_THEMES_DIR
            else:
                theme_dir = settings.THEMES_DIR
            template_dir = os.path.join(theme_dir,
                                get_setting('module', 'theme_editor', 'theme'),
                                'templates')
            template_full_path = os.path.join(template_dir,
                                template_full_name)
            # grab the content from the new-default-template.html
            # first check if there is a customized one on the site
            default_template_name = 'new-default-template.html'
            default_template_path = os.path.join(template_dir,
                                'theme_editor',
                                default_template_name)
            if not os.path.isfile(default_template_path):
                # no customized one found, use the default one
                default_template_path = os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    'templates/theme_editor',
                    default_template_name)
            if os.path.isfile(default_template_path):
                default_content = open(default_template_path).read()
            else:
                default_content = ''
            with open(template_full_path, 'w') as f:
                f.write(default_content)
            if use_s3_storage:
                # django default_storage not set for theme, that's why we cannot use it
                save_file_to_s3(template_full_path)

            ret_dict['created'] = True
            ret_dict['template_name'] = template_full_name
        else:
            ret_dict['err'] = _('Template "%(name)s" already exists' % {'name':template_full_name})


    return HttpResponse(json.dumps(ret_dict))

@login_required
def get_version(request, id):
    version = ThemeFileVersion.objects.get(pk=id)
    return HttpResponse(version.content)


@permission_required('theme_editor.change_themefileversion')
def app_list(request, template_name="theme_editor/app_list.html"):
    app_list = []
    for app in app_templates.keys():
        app_list.append((app, app_templates[app]))
    return render_to_response(template_name, {
        'apps': sorted(app_list, key=lambda app: app[0]),
    }, context_instance=RequestContext(request))


@permission_required('theme_editor.change_themefileversion')
def original_templates(request, app=None, template_name="theme_editor/original_templates.html"):

    current_dir = request.GET.get("dir", '')
    if current_dir:
        current_dir = current_dir.replace('\\', '/')
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

    root = os.path.join(settings.TENDENCI_ROOT, "templates")
    if app:
        root = app_templates[app]

    dirs = get_dir_list(current_dir, ROOT_DIR=root)
    files, non_editable_files = get_file_list(current_dir, ROOT_DIR=root)
    return render_to_response(template_name, {
        'app': app,
        'current_dir': current_dir,
        'prev_dir_name': prev_dir_name,
        'prev_dir': prev_dir,
        'dirs': dirs,
        'files': files,
        'non_editable_files': non_editable_files
    }, context_instance=RequestContext(request))


@permission_required('theme_editor.change_themefileversion')
def copy_to_theme(request, app=None):

    current_dir = request.GET.get("dir", '')
    if current_dir:
        current_dir = current_dir.replace('\\', '/')
        current_dir = current_dir.strip('/')
        current_dir = current_dir.replace('////', '/')
        current_dir = current_dir.replace('///', '/')
        current_dir = current_dir.replace('//', '/')

    chosen_file = request.GET.get("file", '')
    if chosen_file:
        chosen_file = chosen_file.replace('\\', '/')
        chosen_file = chosen_file.strip('/')
        chosen_file = chosen_file.replace('////', '/')
        chosen_file = chosen_file.replace('///', '/')
        chosen_file = chosen_file.replace('//', '/')

    root = os.path.join(settings.TENDENCI_ROOT, "templates")
    if app:
        root = app_templates[app]

    full_filename = os.path.join(root, current_dir, chosen_file)

    if not os.path.isfile(full_filename):
        raise Http404

    copy(chosen_file, current_dir, full_filename)

    msg_string = 'Successfully copied %s/%s to the the theme root' % (current_dir, chosen_file)
    messages.add_message(request, messages.SUCCESS, _(msg_string))

    EventLog.objects.log()
    return redirect('theme_editor.editor')


def delete_file(request):

    # if no permission; raise 403 exception
    if not has_perm(request.user, 'theme_editor.change_themefileversion'):
        raise Http403

    current_dir = request.GET.get("dir", '')
    if current_dir:
        current_dir = current_dir.replace('\\', '/')
        current_dir = current_dir.strip('/')
        current_dir = current_dir.replace('////', '/')
        current_dir = current_dir.replace('///', '/')
        current_dir = current_dir.replace('//', '/')

    if current_dir.startswith('plugins.'):
        current_dir = current_dir.split('plugins.')[1]

    chosen_file = request.GET.get("file", '')
    if chosen_file:
        chosen_file = chosen_file.replace('\\', '/')
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

    if settings.USE_S3_STORAGE:
        delete_file_from_s3(file=settings.AWS_LOCATION + '/' + 'themes/' + get_theme() + '/' + current_dir + chosen_file)

    msg_string = 'Successfully deleted %s/%s.' % (current_dir, chosen_file)
    messages.add_message(request, messages.SUCCESS, _(msg_string))

    EventLog.objects.log()
    return redirect('theme_editor.editor')


@login_required
def upload_file(request):

    if not has_perm(request.user, 'theme_editor.add_themefileversion'):
        raise Http403

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            file_dir = form.cleaned_data['file_dir']
            overwrite = form.cleaned_data['overwrite']
            def callback(file_path, uuid, file_dir=file_dir, overwrite=overwrite):
                file_name = os.path.basename(file_path)
                full_filename = os.path.join(file_dir, file_name)
                if os.path.isfile(full_filename) and not overwrite:
                    msg_string = 'File %s already exists in that folder.' % (file_name)
                    raise uploader.CallbackError(msg_string)
                else:
                    handle_uploaded_file(file_path, file_dir)
                    EventLog.objects.log()
            return uploader.post(request, callback)

        else:  # not valid
            messages.add_message(request, messages.ERROR, form.errors)
            return HttpResponse('invalid', content_type="text/plain")

    return HttpResponseRedirect('/theme-editor/editor/')


@login_required
def theme_picker(request, template_name="theme_editor/theme_picker.html"):
    if not request.user.profile.is_superuser:
        raise Http403

    themes = []
    for theme in theme_choice_list():
        theme_info = ThemeInfo(theme)
        themes.append(theme_info)

    if request.method == "POST":
        selected_theme = request.POST.get('theme')
        call_command('set_theme', selected_theme)
        checklist_update('choose-theme')
        msg_string = "Your theme has been changed to %s." % selected_theme.title()
        messages.add_message(request, messages.SUCCESS, _(msg_string))
        return redirect('home')

    current_theme = get_setting('module', 'theme_editor', 'theme')
    themes = sorted(themes, key=lambda theme: theme.create_dt)

    return render_to_response(template_name, {
        'themes': themes,
        'current_theme': current_theme,
        'theme_choices': theme_choice_list(),
    }, context_instance=RequestContext(request))


@login_required
def theme_color(request):
    if not request.user.profile.is_superuser:
        raise Http403

    if request.is_ajax() and request.method == 'POST':
        if request.POST.get('colors', None):
            color_setting = Setting.objects.get(scope='module',
                                                scope_category='theme',
                                                name='colorvars')
            color_setting.set_value(request.POST.get('colors'))
            color_setting.save()
            checklist_update('customize-color')

            message = _('Successfully updated theme colors.')
            response = json.dumps({'message': message})
            return HttpResponse(response, content_type="application/json")

    raise Http404


@login_required
def get_themes(request, template_name="theme_editor/get_themes.html"):
    if not request.user.profile.is_superuser:
        raise Http403

    if request.is_ajax():
        tracker = UpdateTracker.get_or_create_instance()
        return HttpResponse(tracker.is_updating)

    if request.method == 'POST':
        process = SubProcessManager.set_process(["python", "manage.py", "install_theme", "--all"])
        return render_to_response(template_name, context_instance=RequestContext(request))

    raise Http404
