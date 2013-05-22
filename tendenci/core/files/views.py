import os
import simplejson as json
import urllib2
import mimetypes

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.http import (
    HttpResponseRedirect, HttpResponse, Http404, HttpResponseServerError)
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.middleware.csrf import get_token as csrf_get_token
from django.forms.models import modelformset_factory
from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType

from tendenci.libs.boto_s3.utils import set_s3_file_permission
from tendenci.apps.user_groups.models import Group
from tendenci.core.base.http import Http403
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.decorators import admin_required, is_enabled
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.core.perms.utils import (
    update_perms_and_save, has_perm, has_view_perm, get_query_filters)
from tendenci.core.categories.forms import CategoryForm
from tendenci.core.categories.models import Category
from tendenci.core.event_logs.models import EventLog
from tendenci.core.theme.shortcuts import themed_response as render_to_response
from tendenci.core.files.cache import FILE_IMAGE_PRE_KEY
from tendenci.core.files.models import File
from tendenci.core.files.utils import get_image, aspect_ratio, generate_image_cache_key
from tendenci.core.files.forms import FileForm, MostViewedForm, FileSearchForm, SwfFileForm


@is_enabled('files')
def details(request, id, size=None, crop=False, quality=90, download=False, constrain=False, template_name="files/details.html"):
    """
    Return an image response after paramters have been applied.
    """
    cache_key = generate_image_cache_key(
        file=id,
        size=size,
        pre_key=FILE_IMAGE_PRE_KEY,
        crop=crop,
        unique_key=id,
        quality=quality,
        constrain=constrain)

    cached_image = cache.get(cache_key)
    if cached_image:
        return redirect(cached_image)

    file = get_object_or_404(File, pk=id)

    # basic permissions
    if not has_view_perm(request.user, 'files.view_file', file):
        raise Http403

    # extra permission
    if not file.is_public:
        if not request.user.is_authenticated():
            raise Http403

    # if string and digit convert to integer
    if isinstance(quality, basestring) and quality.isdigit():
        quality = int(quality)

    # get image binary
    try:
        data = file.file.read()
        file.file.close()
    except IOError:  # no such file or directory
        raise Http404

    if download:  # log download
        attachment = u'attachment;'
        EventLog.objects.log(**{
            'event_id': 185000,
            'event_data': '%s %s (%d) dowloaded by %s' % (file.type(), file._meta.object_name, file.pk, request.user),
            'description': '%s downloaded' % file._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': file,
        })
    else:  # log view
        attachment = u''
        if file.type() != 'image':
            EventLog.objects.log(**{
                'event_id': 186000,
                'event_data': '%s %s (%d) viewed by %s' % (file.type(), file._meta.object_name, file.pk, request.user),
                'description': '%s viewed' % file._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': file,
            })

    # if image size specified
    if file.type() == 'image' and size:  # if size specified

        if file.ext() in ('.tif', '.tiff'):
            raise Http404  # tifs cannot (currently) be viewed via browsers

        size = [int(s) if s.isdigit() else 0 for s in size.split('x')]
        size = aspect_ratio(file.image_dimensions(), size, constrain)

        # check for dimensions
        # greater than zero
        if not all(size):
            raise Http404

        # gets resized image from cache or rebuilds
        image = get_image(file.file, size, FILE_IMAGE_PRE_KEY, cache=True, crop=crop, quality=quality, unique_key=None)
        response = HttpResponse(mimetype=file.mime_type())
        response['Content-Disposition'] = '%s filename=%s' % (attachment, file.get_name())

        params = {'quality': quality}
        if image.format == 'GIF':
            params['transparency'] = 0

        image.save(response, image.format, **params)

        if file.is_public_file():
            file_name = "%s%s" % (file.get_name(), ".jpg")
            file_path = 'cached%s%s' % (request.path, file_name)
            default_storage.save(file_path, ContentFile(response.content))
            full_file_path = "%s%s" % (settings.MEDIA_URL, file_path)
            cache.set(cache_key, full_file_path)
            cache_group_key = "files_cache_set.%s" % file.pk
            cache_group_list = cache.get(cache_group_key)

            if cache_group_list is None:
                cache.set(cache_group_key, [cache_key])
            else:
                cache_group_list += [cache_key]
                cache.set(cache_group_key, cache_group_list)

        return response

    if file.is_public_file():
        cache.set(cache_key, file.get_file_public_url())
        set_s3_file_permission(file.file, public=True)
        cache_group_key = "files_cache_set.%s" % file.pk
        cache_group_list = cache.get(cache_group_key)

        if cache_group_list is None:
            cache.set(cache_group_key, [cache_key])
        else:
            cache_group_list += cache_key
            cache.set(cache_group_key, cache_group_list)

    # set mimetype
    if file.mime_type():
        response = HttpResponse(data, mimetype=file.mime_type())
    else:
        raise Http404

    # return response
    if file.get_name().endswith(file.ext()):
        response['Content-Disposition'] = '%s filename=%s' % (attachment, file.get_name())
    else:
        response['Content-Disposition'] = '%s filename=%s' % (attachment, file.get_name_ext())
    return response


@is_enabled('files')
@login_required
def search(request, template_name="files/search.html"):
    """
    This page lists out all files from newest to oldest.
    If a search index is available, this page will also
    have the option to search through files.
    """
    query = u''
    category = u''
    sub_category = u''
    group = None

    has_index = get_setting('site', 'global', 'searchindex')
    form = FileSearchForm(request.GET)

    if form.is_valid():
        query = form.cleaned_data['q']
        category = form.cleaned_data['category']
        sub_category = form.cleaned_data['sub_category']
        group = form.cleaned_data['group']

    if has_index and query:
        files = File.objects.search(query, user=request.user)
        if category:
            files = files.filter(category=category)
        if sub_category:
            files = files.filter(sub_category=sub_category)
    else:
        filters = get_query_filters(request.user, 'files.view_file')
        files = File.objects.filter(filters).distinct()
        if category:
            files = files.filter(categories__category__name=category)
        if sub_category:
            files = files.filter(categories__parent__name=sub_category)

    if group:
        files = files.filter(group_id=group)

    files = files.order_by('-update_dt')

    EventLog.objects.log()

    return render_to_response(
        template_name, {
            'files': files,
            'form': form,
        }, context_instance=RequestContext(request))


def search_redirect(request):
    return HttpResponseRedirect(reverse('files'))


@is_enabled('files')
def print_view(request, id, template_name="files/print-view.html"):
    file = get_object_or_404(File, pk=id)

    # check permission
    if not has_view_perm(request.user, 'files.view_file', file):
        raise Http403

    return render_to_response(
        template_name, {
            'file': file
        }, context_instance=RequestContext(request))


@is_enabled('files')
@login_required
def edit(request, id, form_class=FileForm, category_form_class=CategoryForm, template_name="files/edit.html"):
    file = get_object_or_404(File, pk=id)

    # check permission
    if not has_perm(request.user, 'files.change_file', file):
        raise Http403

    content_type = get_object_or_404(ContentType, app_label='files', model='file')

    #setup categories
    category = Category.objects.get_for_object(file, 'category')
    sub_category = Category.objects.get_for_object(file, 'sub_category')

    initial_category_form_data = {
        'app_label': 'files',
        'model': 'file',
        'pk': file.pk,
        'category': getattr(category, 'name', '0'),
        'sub_category': getattr(sub_category, 'name', '0')
    }

    if request.method == "POST":

        form = form_class(request.POST, request.FILES, instance=file, user=request.user)
        categoryform = category_form_class(content_type, request.POST, initial=initial_category_form_data, prefix='category')

        if form.is_valid() and categoryform.is_valid():
            file = form.save(commit=False)

            # update all permissions and save the model
            file = update_perms_and_save(request, form, file)

            #setup categories
            category = Category.objects.get_for_object(file, 'category')
            sub_category = Category.objects.get_for_object(file, 'sub_category')

            ## update the category of the file
            category_removed = False
            category = categoryform.cleaned_data['category']
            if category != '0':
                Category.objects.update(file, category, 'category')
            else:  # remove
                category_removed = True
                Category.objects.remove(file, 'category')
                Category.objects.remove(file, 'sub_category')

            if not category_removed:
                # update the sub category of the article
                sub_category = categoryform.cleaned_data['sub_category']
                if sub_category != '0':
                    Category.objects.update(file, sub_category, 'sub_category')
                else:  # remove
                    Category.objects.remove(file, 'sub_category')

            file.save()

            return HttpResponseRedirect(reverse('file.search'))
    else:
        form = form_class(instance=file, user=request.user)
        categoryform = category_form_class(content_type, initial=initial_category_form_data, prefix='category')

    return render_to_response(
        template_name, {
            'file': file,
            'form': form,
            'categoryform': categoryform,
        }, context_instance=RequestContext(request))


@is_enabled('files')
@login_required
def bulk_add(request, template_name="files/bulk-add.html"):
    if not has_perm(request.user, 'files.add_file'):
        raise Http403

    FileFormSet = modelformset_factory(
        File,
        form=FileForm,
        can_delete=True,
        fields=(
            'name',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
        ),
        extra=0
    )
    if request.method == "POST":
        # Setup formset html for json response
        file_list = []
        file_formset = FileFormSet(request.POST)
        if file_formset.is_valid():
            file_formset.save()
        else:
            # Handle formset errors
            return render_to_response(template_name, {
                'file_formset': file_formset,
            }, context_instance=RequestContext(request))

        formset_edit = True

        # Handle existing files.  Instance returned by file_formset.save() is not enough
        for num in xrange(file_formset.total_form_count()):
            key = 'form-' + str(num) + '-id'
            if request.POST.get(key):
                file_list.append(request.POST.get(key))
        # Handle new file uploads
        for file in request.FILES.getlist('files'):
            newFile = File(file=file)
            # set up the user information
            newFile.creator = request.user
            newFile.creator_username = request.user.username
            newFile.owner = request.user
            newFile.owner_username = request.user.username
            newFile.save()
            file_list.append(newFile.id)
            formset_edit = False
        # Redirect if form_set is edited i.e. not a file select or drag event
        if formset_edit:
            return HttpResponseRedirect(reverse('file.search'))

        # Handle json response
        file_qs = File.objects.filter(id__in=file_list)
        file_formset = FileFormSet(queryset=file_qs)
        html = render_to_response(
            'files/file-formset.html', {
                'file_formset': file_formset,
            }, context_instance=RequestContext(request)).content

        data = {'form_set': html}
        response = JSONResponse(data, {}, "application/json")
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    else:
        file_formset = FileFormSet({
            'form-TOTAL_FORMS': u'0',
            'form-INITIAL_FORMS': u'0',
            'form-MAX_NUM_FORMS': u'',
        })

    return render_to_response(
        template_name, {
            'file_formset': file_formset,
        }, context_instance=RequestContext(request))


@is_enabled('files')
@login_required
def add(request, form_class=FileForm, category_form_class=CategoryForm, template_name="files/add.html"):
    # check permission
    if not has_perm(request.user, 'files.add_file'):
        raise Http403

    content_type = get_object_or_404(ContentType, app_label='files', model='file')

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, user=request.user)
        categoryform = category_form_class(content_type, request.POST, prefix='category')
        if form.is_valid() and categoryform.is_valid():
            file = form.save(commit=False)

            # set up the user information
            file.creator = request.user
            file.creator_username = request.user.username
            file.owner = request.user
            file.owner_username = request.user.username
            file.save()

            #setup categories
            category = Category.objects.get_for_object(file, 'category')
            sub_category = Category.objects.get_for_object(file, 'sub_category')

            ## update the category of the file
            category_removed = False
            category = categoryform.cleaned_data['category']
            if category != '0':
                Category.objects.update(file, category, 'category')
            else:  # remove
                category_removed = True
                Category.objects.remove(file, 'category')
                Category.objects.remove(file, 'sub_category')

            if not category_removed:
                # update the sub category of the article
                sub_category = categoryform.cleaned_data['sub_category']
                if sub_category != '0':
                    Category.objects.update(file, sub_category, 'sub_category')
                else:  # remove
                    Category.objects.remove(file, 'sub_category')

            #Save relationships
            file.save()

            # assign creator permissions
            ObjectPermission.objects.assign(file.creator, file)

            return HttpResponseRedirect(reverse('file.search'))
    else:
        initial_category_form_data = {
            'app_label': 'files',
            'model': 'file',
            'pk': 0,  # not used for this view but is required for the form
        }
        form = form_class(user=request.user)
        if 'group' in form.fields:
            form.fields['group'].initial = Group.objects.get_initial_group_id()
        categoryform = category_form_class(content_type, initial=initial_category_form_data, prefix='category')
    return render_to_response(
        template_name, {
            'form': form,
            'categoryform': categoryform,
        }, context_instance=RequestContext(request))


@is_enabled('files')
@login_required
def delete(request, id, template_name="files/delete.html"):
    file = get_object_or_404(File, pk=id)

    # check permission
    if not has_perm(request.user, 'files.delete_file'):
        raise Http403

    if request.method == "POST":
        file.delete()

        if 'ajax' in request.POST:
            return HttpResponse('Ok')
        else:
            return HttpResponseRedirect(reverse('file.search'))

    return render_to_response(
        template_name, {
            'file': file
        }, context_instance=RequestContext(request))


@login_required
def tinymce(request, template_name="files/templates/tinymce.html"):
    """
    TinyMCE Insert/Edit images [Window]
    Passes in a list of files associated w/ "this" object
    Examples of "this": Articles, Pages, Releases module
    """
    from django.contrib.contenttypes.models import ContentType
    params = {'app_label': 0, 'model': 0, 'instance_id': 0}
    files = File.objects.none()  # EmptyQuerySet
    all_files = None

    # if all required parameters are in the GET.keys() list
    if not set(params.keys()) - set(request.GET.keys()):

        for item in params:
            params[item] = request.GET[item]

        try:  # get content type
            contenttype = ContentType.objects.get(app_label=params['app_label'], model=params['model'])

            instance_id = params['instance_id']
            if instance_id == 'undefined':
                instance_id = 0

            files = File.objects.filter(
                content_type=contenttype,
                object_id=instance_id
            )

            for media_file in files:
                file, ext = os.path.splitext(media_file.file.url)
                media_file.file.url_thumbnail = '%s_thumbnail%s' % (file, ext)
                media_file.file.url_medium = '%s_medium%s' % (file, ext)
                media_file.file.url_large = '%s_large%s' % (file, ext)
        except ContentType.DoesNotExist:
            raise Http404

    return render_to_response(
        template_name, {
            "media": files,
            "all_media": all_files,
            'csrf_token': csrf_get_token(request),
        }, context_instance=RequestContext(request))


def swfupload(request):
    """
    Handles swfupload.
    Saves file in session.
    File is coupled with object on post_save signal.
    """
    import re
    from django.contrib.contenttypes.models import ContentType

    if request.method == "POST":

        form = SwfFileForm(request.POST, request.FILES, user=request.user)

        if not form.is_valid():
            return HttpResponseServerError(
                str(form._errors), mimetype="text/plain")

        app_label = request.POST['storme_app_label']
        model = unicode(request.POST['storme_model']).lower()
        object_id = int(request.POST['storme_instance_id'])

        if object_id == 'undefined':
            object_id = 0

        try:
            file = form.save(commit=False)
            file.name = re.sub(r'[^a-zA-Z0-9._]+', '-', file.file.name)
            file.object_id = object_id
            file.content_type = ContentType.objects.get(app_label=app_label, model=model)
            file.owner = request.user
            file.creator = request.user
            file.is_public = True
            file.status = True
            file.allow_anonymous_view = True
            file.save()
        except Exception, e:
            print e

        d = {
            "id": file.id,
            "name": file.name,
            "url": file.file.url,
        }

        return HttpResponse(json.dumps([d]), mimetype="text/plain")


@login_required
def tinymce_upload_template(request, id, template_name="files/templates/tinymce_upload.html"):
    file = get_object_or_404(File, pk=id)
    return render_to_response(
        template_name, {
            'file': file
        }, context_instance=RequestContext(request))


@is_enabled('files')
@login_required
@admin_required
def report_most_viewed(request, form_class=MostViewedForm, template_name="files/reports/most_viewed.html"):
    """
    Displays a table of files sorted by views/downloads.
    """
    from django.db.models import Count
    from datetime import date
    from dateutil.relativedelta import relativedelta

    start_dt = date.today() + relativedelta(months=-2)
    end_dt = date.today()
    file_type = 'all'

    form = form_class(
        initial={
            'start_dt': start_dt.strftime('%m/%d/%Y'),
            'end_dt': end_dt.strftime('%m/%d/%Y'),
        }
    )

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            start_dt = form.cleaned_data['start_dt']
            end_dt = form.cleaned_data['end_dt']
            file_type = form.cleaned_data['file_type']

    event_logs = EventLog.objects.values('object_id').filter(
        event_id__in=(185000, 186000), create_dt__range=(start_dt, end_dt))
    event_logs = event_logs | EventLog.objects.values('object_id').filter(
        application='files', action='details', create_dt__range=(start_dt, end_dt))

    if file_type != 'all':
        event_logs = event_logs.filter(event_data__icontains=file_type)

    event_logs = event_logs.annotate(count=Count('object_id')).order_by('-count')

    EventLog.objects.log()

    return render_to_response(
        template_name, {
            'form': form,
            'event_logs': event_logs
        }, context_instance=RequestContext(request))


def display_less(request, path):
    """
    Display the .less files
    """
    content = ''
    if path:
        full_path = '%s/%s.less' % (settings.S3_SITE_ROOT_URL, path)
        url_obj = urllib2.urlopen(full_path)
        content = url_obj.read()
    return HttpResponse(content, mimetype="text/css")


def redirect_to_s3(request, path, file_type='themes'):
    """
    Redirect to S3
    """
    if path:
        if file_type == 'static':
            # static files such as tinymce and webfonts need to be served internally.
            full_path = '%s/%s' % (settings.STATIC_ROOT, path)
            if not os.path.isfile(full_path):
                raise Http404
            with open(full_path) as f:
                content = f.read()
                if os.path.splitext(full_path)[1] == '.css':
                    content_type = 'text/css'
                else:
                    content_type = mimetypes.guess_type(full_path)[0]
                return HttpResponse(content, mimetype=content_type)
        else:
            url = '%s/%s' % (settings.THEMES_DIR, path)
        return HttpResponseRedirect(url)
    raise Http404


class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self, obj='', json_opts={}, mimetype="application/json", *args, **kwargs):
        content = simplejson.dumps(obj, **json_opts)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)
