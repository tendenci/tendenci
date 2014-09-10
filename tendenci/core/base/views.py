# python
from decimal import Decimal
import datetime
import time
import re
from PIL import Image as Pil
import os
import mimetypes
import shutil
import subprocess
import zipfile
import xmlrpclib

# django
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import get_template
from django.shortcuts import redirect
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib import messages
from django.views.i18n import set_language as dj_set_language
from django.utils.translation import check_for_language
from django.utils.translation import ugettext_lazy as _
# local
from tendenci import __version__ as version
from tendenci.core.base.cache import IMAGE_PREVIEW_CACHE
from tendenci.core.base.decorators import password_required
from tendenci.core.base.forms import PasswordForm, AddonUploadForm
from tendenci.core.base.models import UpdateTracker, ChecklistItem
from tendenci.core.base.managers import SubProcessManager
from tendenci.core.perms.decorators import superuser_required
from tendenci.core.theme.shortcuts import themed_response as render_to_response
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.theme.utils import get_theme_info

BASEFILE_EXTENSIONS = (
    'txt',
    'xml',
    'kml',
)

@login_required
def set_language(request):
    """
    It does everything in the django set_language, plus assigning language
    to request.user.profile.

    Below is the behavior of django set_languate:

    Redirect to a given url while setting the chosen language in the
    session or cookie. The url and the language code need to be
    specified in the request parameters.

    Since this view changes how the user will see the rest of the site, it must
    only be accessed as a POST request. If called as a GET request, it will
    redirect to the page in the request (the 'next' parameter) without changing
    any state.
    """
    if not settings.USE_I18N:
        raise Http404
    response = dj_set_language(request)
    if request.method == 'POST':
        lang_code = request.POST.get('language', None)
        if lang_code and check_for_language(lang_code):
            profile = request.user.profile
            profile.language = lang_code
            profile.save()
    return response


def image_preview(request, app_label, model, id,  size):
    """
        Grab all image link within a peice of content
        and generate thumbnails of largest image
    """
    # get page object; protect size
    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model)
        instance = content_type.get_object_for_this_type(id=id)
    except:
        return HttpResponseNotFound(_("Image not found."), mimetype="text/plain")

    keys = [settings.CACHE_PRE_KEY, IMAGE_PREVIEW_CACHE, model, str(instance.id), size]
    key = '.'.join(keys)
    response = cache.get(key)
    original_size = size

    if not response:
        from tendenci.core.base.utils import parse_image_sources, make_image_object_from_url, image_rescale

        # set sizes
        size_min = (30,30)
        size_cap = (512,512)

        size_tuple = size.split('x')
        if len(size_tuple) == 2: size = int(size_tuple[0]), int(size_tuple[1])
        else: size = int(size), int(size)

        if size > size_cap: size = size_cap

        image_urls = []

        image = Pil.new('RGBA',size_min)

        # find biggest image, dimension-wise
        for image_url in image_urls:
            image_candidate = make_image_object_from_url(image_url)
            if image_candidate:
                if image_candidate.size > image.size:
                    image = image_candidate

        if image.size[1] > size_min[1]:
        # rescale, convert-to true-colors; return response

            image = image_rescale(image, size)
            if image.mode != "RGB":
                image = image.convert("RGB")

            response = HttpResponse(mimetype='image/jpeg')

            image.save(response, "JPEG", quality=100)

            keys = [settings.CACHE_PRE_KEY, IMAGE_PREVIEW_CACHE, model, str(instance.id), size]
            key = '.'.join(keys)

            cache.set(key, response)
            return response

        else: # raise http 404 error (returns page not found)
            return HttpResponseNotFound(_("Image not found."), mimetype="text/plain")
    else:
        return response


def custom_error(request, template_name="500.html"):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))


def plugin_static_serve(request, plugin, path, show_indexes=False):
    """
    Serve static files below a given point in the directory structure.

    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root' : '/path/to/my/files/'})

    in your URLconf. You must provide the ``document_root`` param. You may
    also set ``show_indexes`` to ``True`` if you'd like to serve a basic index
    of the directory.  This index view will use the template hardcoded below,
    but if you'd like to override it, you can create a template called
    ``static/directory_index.html``.
    """

    import mimetypes
    import os
    import posixpath
    import stat
    import urllib
    from email.Utils import parsedate_tz, mktime_tz

    from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
    from django.utils.http import http_date
    from django.views.static import was_modified_since, directory_index

    from django.conf import settings

    document_root = os.path.join(settings.PROJECT_ROOT,'plugins',plugin,'media')

    # Clean up given path to only allow serving files below document_root.
    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')

    if newpath and path != newpath:
        return HttpResponseRedirect(newpath)
    fullpath = os.path.join(document_root, newpath)

    if os.path.isdir(fullpath):
        if show_indexes:
            return directory_index(newpath, fullpath)
        raise Http404(_("Directory indexes are not allowed here."))
    if not os.path.exists(fullpath):
        raise Http404('"%s" does not exist' % fullpath)

    # Respect the If-Modified-Since header.
    statobj = os.stat(fullpath)
    mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified(mimetype=mimetype)
    contents = open(fullpath, 'rb').read()
    response = HttpResponse(contents, mimetype=mimetype)
    response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
    response["Content-Length"] = len(contents)
    return response


def clear_cache(request):
    cache.clear()
    return redirect('dashboard')


def memcached_status(request):
    try:
        import memcache
    except ImportError:
        raise Http404

    if not request.user.is_authenticated() and request.user.is_superuser:
        raise Http404

    # get first memcached URI
    m = re.match(
        "memcached://([.\w]+:\d+)", settings.CACHE_BACKEND
    )
    if not m:
        raise Http404

    host = memcache._Host(m.group(1))
    host.connect()
    host.send_cmd("stats")

    class Stats:
        pass

    stats = Stats()

    while 1:
        line = host.readline().split(None, 2)
        if line[0] == "END":
            break
        stat, key, value = line
        try:
            # convert to native type, if possible
            value = int(value)
            if key == "uptime":
                value = datetime.timedelta(seconds=value)
            elif key == "time":
                value = datetime.datetime.fromtimestamp(value)
        except ValueError:
            pass
        setattr(stats, key, value)

    host.close_socket()

    return render_to_response('base/memcached_status.html', {
            'stats': stats,
            'hit_rate': 100 * stats.get_hits / stats.cmd_get,
            'time': datetime.datetime.now(), # server time
    })


def feedback(request, template_name="base/feedback.html"):
    # This page is deprecated, but some sites might have the url in their
    # overridden admin bar, so we are leaving it and just raising 404
    raise Http404

    return render_to_response(template_name, {}, context_instance=RequestContext(request))

def homepage(request, template_name="homepage.html"):
    from tendenci.core.event_logs.models import EventLog

    EventLog.objects.log()

    return render_to_response(template_name, {}, context_instance=RequestContext(request))


def robots_txt(request):
    options = ['base/robots_private.txt', 'base/robots_public.txt', 'robots.txt']
    template_name = "robots.txt"

    robots_setting = get_setting('site', 'global', 'robotstxt')
    if robots_setting in options:
        template_name = robots_setting

    site_url = get_setting('site', 'global', 'siteurl')
    return render_to_response(template_name, {'site_url': site_url}, context_instance=RequestContext(request), mimetype="text/plain")


def base_file(request, file_name):
    """
    Renders file_name at url path /file_name
    Only predefined extensions are allowed.
    """
    ext = os.path.splitext(file_name)[1].strip('.')
    if not ext in BASEFILE_EXTENSIONS:
        raise Http404

    try:
        t = get_template(file_name.encode('ascii', 'ignore'))
    except TemplateDoesNotExist:
        raise Http404

    return HttpResponse(t.render(RequestContext(request)))


def exception_test(request):
    raise Exception('Successfully raised the exception test. Boom.')


def timeout_test(request):
    # Sleep for 60 seconds to simulate a long process time
    time.sleep(60)
    raise Http404


def file_display(request, file_path):
    base_name = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(base_name)[0]

    if not mime_type:
        raise Http404

    if not default_storage.exists(file_path):
        raise Http404

    data = default_storage.open(file_path).read()

    response = HttpResponse(data, mimetype=mime_type)
    response['Content-Disposition'] = 'filename=%s' % base_name

    return response


@login_required
def password_again(request, template_name="base/password.html"):
    next = request.GET.get('next')

    if request.method == "POST":
        form = PasswordForm(request.POST, user=request.user)
        if form.is_valid():
            request.session['password_promt'] = dict(
                                    time=int(time.time()),
                                    value=True)
            return redirect(next)
    else:
        form = PasswordForm(user=request.user)

    return render_to_response(template_name, {
        'next': next,
        'form': form,
    }, context_instance=RequestContext(request))


@superuser_required
def checklist(request, template_name="base/checklist.html"):
    theme_info = get_theme_info()
    try:
        checklist_enabled = theme_info['SSU']['checklist']
    except KeyError:
        raise Http404
    if not checklist_enabled:
        raise Http404

    checklist = ChecklistItem.objects.all()

    total_count = checklist.count()
    completed = checklist.filter(done=True)
    completed_count = completed.count()

    percent = (Decimal(completed_count) / Decimal(total_count)) * 100

    return render_to_response(template_name,
                              {'checklist': checklist, "percent": percent},
                              context_instance=RequestContext(request))


@superuser_required
def addon_upload(request, template_name="base/addon_upload.html"):
    from tendenci.core.event_logs.models import EventLog

    form = AddonUploadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            identifier = str(int(time.time()))
            temp_file_path = 'uploads/addons/%s_%s' % (identifier, form.cleaned_data['addon'])
            default_storage.save(temp_file_path, form.cleaned_data['addon'])
            request.session[identifier] = temp_file_path

            EventLog.objects.log(
                event_data='%s uploaded by %s' % (form.cleaned_data['addon'], request.user),
                description='%s' % form.cleaned_data['addon'])

            return redirect('addon.upload.preview', identifier)

    return render_to_response(template_name, {'form': form},
                              context_instance=RequestContext(request))


@superuser_required
def addon_upload_preview(request, sid, template_name="base/addon_upload_preview.html"):

    if not sid in request.session:
        raise Http404
    path = request.session[sid]

    addon_zip = zipfile.ZipFile(default_storage.open(path))
    addon_name = addon_zip.namelist()[0]
    addon_name = addon_name.strip('/')
    if not os.path.isdir(os.path.join(settings.SITE_ADDONS_PATH, addon_name)):
        subprocess.Popen(["python", "manage.py",
                          "upload_addon",
                          '--zip_path=%s' % path])
        return redirect('addon.upload.process', sid)

    if request.method == "POST":
        shutil.rmtree(os.path.join(settings.SITE_ADDONS_PATH, addon_name))
        subprocess.Popen(["python", "manage.py",
                          "upload_addon",
                          '--zip_path=%s' % path])
        return redirect('addon.upload.process', sid)

    return render_to_response(template_name, {'addon_name': addon_name, 'sid':sid },
                              context_instance=RequestContext(request))


@superuser_required
def addon_upload_process(request, sid, template_name="base/addon_upload_process.html"):

    if not sid in request.session:
        raise Http404
    path = request.session[sid]

    if not default_storage.exists(path):
        messages.add_message(request, messages.SUCCESS, _('Addon upload complete.'))
        del request.session[sid]
        return redirect('dashboard')

    return render_to_response(template_name, {'sid': sid },
                              context_instance=RequestContext(request))


def addon_upload_check(request, sid):

    if not sid in request.session:
        raise Http404
    path = request.session[sid]

    finished = False
    if not default_storage.exists(path):
        finished = True

    return HttpResponse(finished)


@superuser_required
@password_required
def update_tendenci(request, template_name="base/update.html"):
    if request.method == "POST":
        process = SubProcessManager.set_process(["python", "manage.py", "update_tendenci",
                                                 "--user=%s" % request.user.id])
        return redirect('update_tendenci.confirmation')

    pypi = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
    latest_version = pypi.package_releases('tendenci')[0]

    update_available = False
    if latest_version != version:
        update_available = True

    return render_to_response(template_name, {
        'latest_version': latest_version,
        'update_available': update_available,
    }, context_instance=RequestContext(request))


@superuser_required
@password_required
def update_tendenci_confirmation(request, template_name="base/update_confirmation.html"):
    return render_to_response(template_name, context_instance=RequestContext(request))
