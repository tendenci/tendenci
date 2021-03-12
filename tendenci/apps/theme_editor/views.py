from builtins import str
import os
import shutil
import subprocess

from django.shortcuts import redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
import simplejson as json
from django.core.management import call_command
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.libs.utils import python_executable
from tendenci.apps.base.http import Http403
from tendenci.apps.base.models import UpdateTracker
from tendenci.apps.base.utils import get_template_list, checklist_update
from tendenci.apps.site_settings.models import Setting
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.theme.utils import (get_theme, get_active_theme, get_theme_root, is_valid_theme,
                                       is_base_theme, theme_choices, get_theme_search_order)
from tendenci.libs.boto_s3.utils import delete_file_from_s3
from tendenci.apps.theme_editor.models import ThemeFileVersion
from tendenci.apps.theme_editor.forms import (FileForm, ThemeNameForm, ThemeSelectForm,
                                              UploadForm, AddTemplateForm)
from tendenci.apps.theme_editor.utils import (is_valid_path, is_theme_read_only, ThemeInfo,
                                              app_templates, get_dir_list, get_file_list,
                                              get_file_content, get_all_files_list,
                                              copy_file_to_theme)
from tendenci.libs.boto_s3.utils import save_file_to_s3
from tendenci.libs.uploader import uploader

DEFAULT_FILE = 'templates/homepage.html'


@permission_required('theme_editor.change_themefileversion')
def edit_file(request, form_class=FileForm, template_name="theme_editor/index.html"):

    selected_theme = request.GET.get("theme_edit", get_theme())
    if not is_valid_theme(selected_theme):
        raise Http404(_('Specified theme does not exist'))

    # get the default file and clean up any input
    default_file = request.GET.get("file", DEFAULT_FILE)
    if default_file:
        default_file = default_file.replace('\\', '/')
        default_file = default_file.strip('/')
        default_file = default_file.replace('////', '/')
        default_file = default_file.replace('///', '/')
        default_file = default_file.replace('//', '/')

    theme_root = get_theme_root(selected_theme)
    if not is_valid_path(theme_root, default_file):
        raise Http403

    theme_read_only = is_theme_read_only(selected_theme)

    if request.is_ajax() and request.method == "POST":
        if theme_read_only:
            raise Http403
        file_form = form_class(request.POST)
        response_status = 'FAIL'
        response_message = _('Cannot update file.')
        if file_form.is_valid():
            if file_form.save(theme_root, selected_theme, default_file, request):
                response_status = 'SUCCESS'
                response_message = str(_('Your changes have been saved.'))
                EventLog.objects.log()
        response = json.dumps({'status': response_status, 'message': response_message})
        return HttpResponse(response, content_type='application/json')

    is_file = os.path.isfile(os.path.join(theme_root, default_file))
    is_dir = os.path.isdir(os.path.join(theme_root, default_file))
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
    # make sure the path is still valid after stripping off the file name
    if not is_valid_path(theme_root, pwd):
        raise Http403

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

    # get the directory list
    dirs = get_dir_list(theme_root, pwd)

    # get the file list
    files, non_editable_files = get_file_list(theme_root, pwd)

    all_files_folders = get_all_files_list(theme_root, selected_theme)

    # non-deletable files
    non_deletable_files = ['homepage.html', 'default.html', 'footer.html', 'header.html', 'sidebar.html', 'nav.html', 'styles.less', 'styles.css']

    # get the number of themes in the themes directory on the site
    theme_count = len([i for i in theme_choices()])

    # get a list of revisions
    archives = ThemeFileVersion.objects.filter(relative_file_path=current_file_path).order_by("-create_dt")

    # New templates created by clicking the New Template" button are blank.
    # Add a space for the blank template to make it editable.
    content = get_file_content(theme_root, selected_theme, current_file_path) or ' '
    file_form = form_class({'content': content})
    
    # if template caching is on, a site reload is required
    reload_required = 'CachedLoader' in settings.TEMPLATES[0]['OPTIONS']['loaders'][0][0]

    return render_to_resp(request=request, template_name=template_name, context={
        'file_form': file_form,
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
        'theme_read_only': theme_read_only,
        'can_copy_theme': (not is_base_theme(selected_theme)),
        'all_files_folders': all_files_folders,
        'ext' : ext,
        'stylesheets' : stylesheets,
        'reload_required': reload_required
    })


@login_required
def theme_copy(request, form_class=ThemeNameForm):
    if not request.user.profile.is_superuser:
        raise Http403

    selected_theme = request.GET.get("theme_edit", get_theme())
    if not is_valid_theme(selected_theme):
        raise Http404(_('Specified theme does not exist'))
    theme_root = get_theme_root(selected_theme)

    form = form_class(request.POST or None)
    ret_dict = {'success': False, 'err': ''}

    if form.is_valid():
        new_theme_name = form.cleaned_data['theme_name']
        if is_valid_theme(new_theme_name):
            ret_dict['err'] = _('Theme "%(name)s" already exists' % {'name': new_theme_name})
            return HttpResponse(json.dumps(ret_dict))
        if not is_valid_path(settings.ORIGINAL_THEMES_DIR, new_theme_name):
            raise Http403
        new_theme_root = get_theme_root(new_theme_name)
        shutil.copytree(theme_root, new_theme_root, symlinks=False)
        ret_dict['success'] = True
        EventLog.objects.log()
    #else:
    #    ret_dict['err'] = form.errors.as_json()

    return HttpResponse(json.dumps(ret_dict))


@login_required
def theme_rename(request, form_class=ThemeNameForm):
    if not request.user.profile.is_superuser:
        raise Http403

    selected_theme = request.GET.get("theme_edit", get_theme())
    if not is_valid_theme(selected_theme):
        raise Http404(_('Specified theme does not exist'))
    if is_theme_read_only(selected_theme):
        raise Http403
    theme_root = get_theme_root(selected_theme)

    form = form_class(request.POST or None)
    ret_dict = {'success': False, 'err': ''}

    if form.is_valid():
        new_theme_name = form.cleaned_data['theme_name']
        if is_valid_theme(new_theme_name):
            ret_dict['err'] = _('Theme "%(name)s" already exists' % {'name': new_theme_name})
            return HttpResponse(json.dumps(ret_dict))
        if not is_valid_path(settings.ORIGINAL_THEMES_DIR, new_theme_name):
            raise Http403
        new_theme_root = get_theme_root(new_theme_name)
        shutil.move(theme_root, new_theme_root)
        ret_dict['success'] = True
        EventLog.objects.log()
    #else:
    #    ret_dict['err'] = form.errors.as_json()

    return HttpResponse(json.dumps(ret_dict))


@login_required
def theme_delete(request):
    if not request.user.profile.is_superuser:
        raise Http403

    selected_theme = request.GET.get("theme_edit", get_theme())
    if not is_valid_theme(selected_theme):
        raise Http404(_('Specified theme does not exist'))
    if is_theme_read_only(selected_theme):
        raise Http403

    shutil.rmtree(get_theme_root(selected_theme))

    if settings.USE_S3_STORAGE:
        delete_file_from_s3(file=settings.AWS_LOCATION + '/' + settings.THEME_S3_PATH + '/' + selected_theme)

    msg_string = 'Successfully deleted %s.' % (selected_theme)
    messages.add_message(request, messages.SUCCESS, _(msg_string))

    EventLog.objects.log()
    return redirect('theme_editor.editor')


@permission_required('theme_editor.change_themefileversion')
def create_new_template(request, form_class=AddTemplateForm):
    """
    Create a new blank template for a given template name
    """
    selected_theme = request.GET.get("theme_edit", get_theme())
    if not is_valid_theme(selected_theme):
        raise Http404(_('Specified theme does not exist'))
    if is_theme_read_only(selected_theme):
        raise Http403

    form = form_class(request.POST or None)
    ret_dict = {'created': False, 'err': ''}

    if form.is_valid():
        template_name = form.cleaned_data['template_name'].strip()
        template_full_name = 'default-%s.html' % template_name
        existing_templates = [t[0] for t in get_template_list()]
        if template_full_name not in existing_templates:
            # create a new template and assign default content
            theme_root = get_theme_root(selected_theme)
            template_dir = os.path.join(theme_root, 'templates')
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
            if settings.USE_S3_STORAGE:
                s3_path = os.path.join(settings.THEME_S3_PATH, selected_theme, 'templates', template_full_name)
                save_file_to_s3(template_full_path, dest_path=s3_path, public=False)
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

    selected_theme = request.GET.get("theme_edit", get_theme())
    if not is_valid_theme(selected_theme):
        raise Http404(_('Specified theme does not exist'))
    if is_theme_read_only(selected_theme):
        raise Http403

    theme_list = get_theme_search_order(selected_theme)[1:]
    app_list = app_templates.keys()
    return render_to_resp(request=request, template_name=template_name, context={
        'current_theme': selected_theme,
        'apps': theme_list + sorted(app_list, key=lambda app: app[0]),
    })


@permission_required('theme_editor.change_themefileversion')
def original_templates(request, template_name="theme_editor/original_templates.html"):

    selected_theme = request.GET.get("theme_edit", get_theme())
    if not is_valid_theme(selected_theme):
        raise Http404(_('Specified theme does not exist'))
    if is_theme_read_only(selected_theme):
        raise Http403

    app = request.GET.get("app", None)

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

    if app in app_templates:
        root = app_templates[app]
    elif is_valid_theme(app):
        root = os.path.join(get_theme_root(app), 'templates')
    else:
        if '/' in app and app.split('/')[0] == 'builtin':
            builtin_base_name = app.split('/')[1]
            root = os.path.join(settings.TENDENCI_ROOT, "themes/{}/templates".format(builtin_base_name))
        else:
            raise Http404(_('Specified theme or app does not exist'))

    if not is_valid_path(root, current_dir):
        raise Http403

    dirs = get_dir_list(root, current_dir)
    files, non_editable_files = get_file_list(root, current_dir)
    return render_to_resp(request=request, template_name=template_name, context={
        'current_theme': selected_theme,
        'app': app,
        'current_dir': current_dir,
        'prev_dir_name': prev_dir_name,
        'prev_dir': prev_dir,
        'dirs': dirs,
        'files': files,
        'non_editable_files': non_editable_files,
    })


@permission_required('theme_editor.change_themefileversion')
def copy_to_theme(request):

    selected_theme = request.GET.get("theme_edit", get_theme())
    if not is_valid_theme(selected_theme):
        raise Http404(_('Specified theme does not exist'))
    if is_theme_read_only(selected_theme):
        raise Http403

    app = request.GET.get("app", None)

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

    if app in app_templates:
        root = app_templates[app]
    elif is_valid_theme(app):
        root = os.path.join(get_theme_root(app), 'templates')
    else:
        if '/' in app and app.split('/')[0] == 'builtin':
            builtin_base_name = app.split('/')[1]
            root = os.path.join(settings.TENDENCI_ROOT, "themes/{}/templates".format(builtin_base_name))
        else:
            raise Http404(_('Specified theme or app does not exist'))

    if (not is_valid_path(root, current_dir) or
        not is_valid_path(root, os.path.join(current_dir, chosen_file))):
        raise Http403

    full_filename = os.path.join(root, current_dir, chosen_file)

    if not os.path.isfile(full_filename):
        raise Http404

    copy_file_to_theme(full_filename, selected_theme, os.path.join('templates', current_dir), chosen_file)

    msg_string = 'Successfully copied %s/%s to theme' % (current_dir, chosen_file)
    messages.add_message(request, messages.SUCCESS, _(msg_string))

    EventLog.objects.log()
    return redirect('theme_editor.editor')


@permission_required('theme_editor.change_themefileversion')
def delete_file(request):

    selected_theme = request.GET.get("theme_edit", get_theme())
    if not is_valid_theme(selected_theme):
        raise Http404(_('Specified theme does not exist'))
    if is_theme_read_only(selected_theme):
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

    theme_root = get_theme_root(selected_theme)

    if (not is_valid_path(theme_root, current_dir) or
        not is_valid_path(theme_root, os.path.join(current_dir, chosen_file))):
        raise Http403

    full_filename = os.path.join(theme_root, current_dir, chosen_file)

    if not os.path.isfile(full_filename):
        raise Http404

    os.remove(full_filename)

    if settings.USE_S3_STORAGE:
        s3_path = selected_theme + '/' + current_dir + chosen_file
        s3_full_path = settings.AWS_LOCATION + '/' + settings.THEME_S3_PATH + '/' + s3_path
        delete_file_from_s3(file=s3_full_path)
        cache_key = ".".join([settings.SITE_CACHE_KEY, 'theme', s3_path])
        cache.delete(cache_key)

    msg_string = 'Successfully deleted %s/%s.' % (current_dir, chosen_file)
    messages.add_message(request, messages.SUCCESS, _(msg_string))

    EventLog.objects.log()
    return redirect('theme_editor.editor')


@permission_required('theme_editor.change_themefileversion')
def upload_file(request):

    selected_theme = request.GET.get("theme_edit", get_theme())
    if not is_valid_theme(selected_theme):
        raise Http404(_('Specified theme does not exist'))
    if is_theme_read_only(selected_theme):
        raise Http403

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            file_dir = form.cleaned_data['file_dir']
            overwrite = form.cleaned_data['overwrite']

            def callback(file_path, uuid, selected_theme=selected_theme, file_dir=file_dir, overwrite=overwrite):
                theme_root = get_theme_root(selected_theme)
                file_name = os.path.basename(file_path)
                full_filename = os.path.join(file_dir, file_name)
                if (not is_valid_path(theme_root, file_dir) or
                    not is_valid_path(theme_root, full_filename)):
                    raise Http403
                if os.path.isfile(os.path.join(theme_root, full_filename)) and not overwrite:
                    msg_string = 'File %s already exists in that folder.' % (file_name)
                    raise uploader.CallbackError(msg_string)
                copy_file_to_theme(file_path, selected_theme, file_dir, file_name)
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
    for theme in theme_choices():
        theme_info = ThemeInfo(theme)
        themes.append(theme_info)

    if request.method == "POST":
        selected_theme = request.POST.get('theme')
        if not is_valid_theme(selected_theme):
            raise Http403
        call_command('set_theme', selected_theme)
        checklist_update('choose-theme')
        msg_string = "Your theme has been changed to %s." % selected_theme.title()
        messages.add_message(request, messages.SUCCESS, _(msg_string))
        return redirect('home')

    active_theme = get_active_theme()
    themes = sorted(themes, key=lambda theme: theme.create_dt)

    return render_to_resp(request=request, template_name=template_name, context={
        'themes': themes,
        'current_theme': active_theme,
        'theme_choices': theme_choices(),
    })


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
        subprocess.Popen([python_executable(), "manage.py", "install_theme", "--all"])
        return render_to_resp(request=request, template_name=template_name)

    raise Http404
