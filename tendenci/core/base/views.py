# python
import datetime
import time
import re
import Image as Pil
import os
import mimetypes

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

# local
from tendenci.core.base.cache import IMAGE_PREVIEW_CACHE
from tendenci.core.base.forms import PasswordForm
from tendenci.core.theme.shortcuts import themed_response as render_to_response
from tendenci.core.site_settings.utils import get_setting

BASEFILE_EXTENSIONS = (
    'txt',
    'xml',
    'kml',
)


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
        return HttpResponseNotFound("Image not found.", mimetype="text/plain")
    
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
            return HttpResponseNotFound("Image not found.", mimetype="text/plain")
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
        raise Http404("Directory indexes are not allowed here.")
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
    from tendenci.core.event_logs.models import EventLog
    if not request.user.profile.is_superuser:
        raise Http404
    EventLog.objects.log()
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

    return render_to_response(template_name, {}, context_instance=RequestContext(request), mimetype="text/plain")


def base_file(request, file_name):
    """
    Renders file_name at url path /file_name
    Only predefined extensions are allowed.
    """
    ext = os.path.splitext(file_name)[1].strip('.')
    if not ext in BASEFILE_EXTENSIONS:
        raise Http404

    try:
        t = get_template(file_name)
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
