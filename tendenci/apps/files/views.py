from builtins import str
import os
import simplejson as json
from urllib.request import urlopen
import mimetypes
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.http import (
    HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseForbidden)
import simplejson
from django.urls import reverse
from django.middleware.csrf import get_token as csrf_get_token
from django.forms.models import modelformset_factory
from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from tendenci.libs.boto_s3.utils import set_s3_file_permission
from tendenci.apps.user_groups.models import Group
from tendenci.apps.base.http import Http403
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.decorators import admin_required, is_enabled
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.perms.utils import (
    update_perms_and_save, has_perm, has_view_perm, get_query_filters)
from tendenci.apps.categories.models import Category
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.files.cache import FILE_IMAGE_PRE_KEY
from tendenci.apps.files.models import File, FilesCategory
from tendenci.apps.files.utils import get_image, aspect_ratio, generate_image_cache_key, get_max_file_upload_size, get_allowed_upload_file_exts
from tendenci.apps.files.forms import FileForm, MostViewedForm, FileSearchForm, FileSearchMinForm, TinymceUploadForm


@is_enabled('files')
def details(request, id, size=None, crop=False, quality=90, download=False, constrain=False, template_name="files/details.html"):
    """
    Return an image response after paramters have been applied.
    """
    file = get_object_or_404(File, pk=id)

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
        if file.type() != 'image':
            # log an event
            EventLog.objects.log(instance=file)
        return redirect('%s%s' % (get_setting('site', 'global', 'siteurl'), cached_image))

    # basic permissions
    if not has_view_perm(request.user, 'files.view_file', file):
        raise Http403

    # extra permission
    if not file.is_public:
        if not request.user.is_authenticated:
            raise Http403

    # if string and digit convert to integer
    if isinstance(quality, str) and quality.isdigit():
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
        response = HttpResponse(content_type=file.mime_type())
        response['Content-Disposition'] = '%s filename="%s"' % (attachment, file.get_name())

        params = {'quality': quality}
        if image.format == 'GIF':
            params['transparency'] = 0

        try:
            image.save(response, image.format, **params)
        except AttributeError:
            return response

        if file.is_public_file():
            file_name = "%s%s" % (file.get_name(), ".jpg")
            file_path = 'cached%s%s' % (request.path, file_name)
            if not default_storage.exists(file_path):
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
        response = HttpResponse(data, content_type=file.mime_type())
    else:
        raise Http404

    # return response
    if file.get_name().endswith(file.ext()):
        response['Content-Disposition'] = '%s filename="%s"' % (attachment, file.get_name())
    else:
        response['Content-Disposition'] = '%s filename="%s"' % (attachment, file.get_name_ext())
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
    category = None
    sub_category = None
    group = None

    form = FileSearchForm(request.GET, **{'user': request.user})

    if form.is_valid():
        query = form.cleaned_data.get('q', '')
        category = form.cleaned_data.get('file_cat', None)
        sub_category = form.cleaned_data.get('file_sub_cat', None)
        group = form.cleaned_data.get('group', None)

    filters = get_query_filters(request.user, 'files.view_file')
    files = File.objects.filter(filters).distinct()
    if query:
        files = files.filter(Q(file__icontains=query)|
                             Q(name__icontains=query)|
                             Q(description__icontains=query)|
                             Q(tags__icontains=query))
    if category:
        files = files.filter(file_cat=category)
    if sub_category:
        files = files.filter(file_sub_cat=sub_category)
    if group:
        files = files.filter(group_id=group)

    files = files.order_by('-update_dt')

    EventLog.objects.log()

    layout = get_setting("module", "files", "layout")
    base_template_path = "files/base.html"
    if layout == 'grid':
        base_template_path = "base-wide.html"

    return render_to_resp(
        request=request, template_name=template_name, context={
            'files': files,
            'form': form,
            'layout': layout,
            'base_template_path': base_template_path,
        })


def search_redirect(request):
    return HttpResponseRedirect(reverse('files'))


@is_enabled('files')
def print_view(request, id, template_name="files/print-view.html"):
    file = get_object_or_404(File, pk=id)

    # check permission
    if not has_view_perm(request.user, 'files.view_file', file):
        raise Http403

    return render_to_resp(
        request=request, template_name=template_name, context={
            'file': file
        })


@is_enabled('files')
@login_required
def edit(request, id, form_class=FileForm, template_name="files/edit.html"):
    file = get_object_or_404(File, pk=id)

    # check permission
    if not has_perm(request.user, 'files.change_file', file):
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=file, user=request.user)

        if form.is_valid():
            file = form.save(commit=False)

            # update all permissions and save the model
            file = update_perms_and_save(request, form, file)

            #setup categories
            category = Category.objects.get_for_object(file, 'category')
            sub_category = Category.objects.get_for_object(file, 'sub_category')

            ## update the category of the file
            category_removed = False
            category = file.file_cat.name if file.file_cat else None
            if category:
                Category.objects.update(file, category, 'category')
            else:  # remove
                category_removed = True
                Category.objects.remove(file, 'category')
                Category.objects.remove(file, 'sub_category')

            if not category_removed:
                # update the sub category of the article
                sub_category = file.file_sub_cat.name if file.file_sub_cat else None
                if sub_category:
                    Category.objects.update(file, sub_category, 'sub_category')
                else:  # remove
                    Category.objects.remove(file, 'sub_category')

            file.save()

            return HttpResponseRedirect(reverse('file.search'))
    else:
        form = form_class(instance=file, user=request.user)

    return render_to_resp(
        request=request, template_name=template_name, context={
            'file': file,
            'form': form,
        })


class FileTinymceCreateView(CreateView):
    model = File
    #fields = ("file",)
    template_name_suffix = '_tinymce_upload_form'
    form_class = TinymceUploadForm

    @method_decorator(is_enabled('files'))
    @method_decorator(login_required)
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if not has_perm(request.user, 'files.add_file'):
            return HttpResponseForbidden()
        return super(FileTinymceCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FileTinymceCreateView, self).get_context_data(**kwargs)
        context['app_label'] = self.request.GET.get('app_label', '')
        context['model'] = self.request.GET.get('model', '')
        context['object_id'] = self.request.GET.get('object_id', 0)
        context['max_file_size'] = get_max_file_upload_size(file_module=True)
        context['upload_type'] = self.request.GET.get('type', '')
        context['accept_file_types'] = '|'.join(x[1:] for x in get_allowed_upload_file_exts(context['upload_type']))

        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(request_data=self.request)
        return kwargs

    def form_valid(self, form):
        app_label = self.request.POST['app_label']
        model = str(self.request.POST['model']).lower()
        try:
            object_id = int(self.request.POST['object_id'])
        except:
            object_id = 0
        self.object = form.save()
        self.object.object_id = object_id
        try:
            self.object.content_type = ContentType.objects.get(app_label=app_label, model=model)
        except ContentType.DoesNotExist:
            self.object.content_type = None
        self.object.creator = self.request.user
        self.object.creator_username = self.request.user.username
        self.object.owner = self.request.user
        self.object.owner_username = self.request.user.username
        self.object.save()
        f = self.object.file
        name = self.object.basename()
        if self.object.f_type == 'image':
            thumbnail_url = reverse('file', args=[self.object.id, '50x50', 'crop', '88'])
        else:
            thumbnail_url = self.object.icon()
        # truncate name to 20 chars length
        if len(name) > 20:
            name = name[:17] + '...'
        data = {'files': [{
            'url': self.object.get_absolute_url(),
            'name': name,
            'type': mimetypes.guess_type(f.path)[0] or 'image/png',
            'thumbnailUrl': thumbnail_url,
            'size': self.object.get_size(),
            'deleteUrl': reverse('file.delete', args=[self.object.pk]),
            'deleteType': 'DELETE',}]
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        data = json.loads(form.errors.as_json()).values()
        errors = '. '.join([x[0]['message'] for x in data])
        data = {'files': [{
                'errors': errors,}]
                }
        return JsonResponse(data)
#         data = json.dumps(form.errors)
#         print('data=', data)
#         return HttpResponse(content=data, status=400, content_type='application/json')


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
            return render_to_resp(request=request, template_name=template_name, context={
                'file_formset': file_formset,
            })

        formset_edit = True

        # Handle existing files.  Instance returned by file_formset.save() is not enough
        for num in range(file_formset.total_form_count()):
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
        html = render_to_resp(
            request=request, template_name='files/file-formset.html', context={
                'file_formset': file_formset,
            }).content

        data = {'form_set': html}
        response = JSONResponse(data, {}, "application/json")
        response['Content-Disposition'] = 'inline; filename="files.json"'
        return response
    else:
        file_formset = FileFormSet({
            'form-TOTAL_FORMS': u'0',
            'form-INITIAL_FORMS': u'0',
            'form-MAX_NUM_FORMS': u'',
        })

    return render_to_resp(
        request=request, template_name=template_name, context={
            'file_formset': file_formset,
        })


@is_enabled('files')
@login_required
def add(request, form_class=FileForm,template_name="files/add.html"):
    # check permission
    if not has_perm(request.user, 'files.add_file'):
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            file = form.save(commit=False)

            # set up the user information
            file.creator = request.user
            file.creator_username = request.user.username
            file.owner = request.user
            file.owner_username = request.user.username
            file.save()

            # update all permissions and save the model
            file = update_perms_and_save(request, form, file)

            #setup categories
            category = Category.objects.get_for_object(file, 'category')
            sub_category = Category.objects.get_for_object(file, 'sub_category')

            ## update the category of the file
            category_removed = False
            category = file.file_cat.name if file.file_cat else u''
            if category:
                Category.objects.update(file, category, 'category')
            else:  # remove
                category_removed = True
                Category.objects.remove(file, 'category')
                Category.objects.remove(file, 'sub_category')

            if not category_removed:
                # update the sub category of the article
                sub_category = file.file_sub_cat.name if file.file_sub_cat else u''
                if sub_category:
                    Category.objects.update(file, sub_category, 'sub_category')
                else:  # remove
                    Category.objects.remove(file, 'sub_category')

            #Save relationships
            file.save()

            # assign creator permissions
            ObjectPermission.objects.assign(file.creator, file)

            return HttpResponseRedirect(reverse('file.search'))
    else:
        form = form_class(user=request.user)
        if 'group' in form.fields:
            form.fields['group'].initial = Group.objects.get_initial_group_id()

    return render_to_resp(
        request=request, template_name=template_name, context={
            'form': form,
        })


@is_enabled('files')
@login_required
def delete(request, id, template_name="files/delete.html"):
    file = get_object_or_404(File, pk=id)

    # check permission
    if not has_perm(request.user, 'files.delete_file'):
        raise Http403

    if request.method in ["POST", 'DELETE']:
        # reassign owner to current user
        file.owner = request.user
        file.owner_username = request.user.username
        file.save()
        file.delete()

        if request.method == 'DELETE':
            # used by tinymce upload
            return HttpResponse('true')

        if 'ajax' in request.POST:
            return HttpResponse('Ok')
        else:
            return HttpResponseRedirect(reverse('file.search'))

    return render_to_resp(
        request=request, template_name=template_name, context={
            'file': file
        })


@is_enabled('files')
@login_required
def tinymce_fb(request, template_name="files/templates/tinymce_fb.html"):
    """
    Get a list of files (images) for tinymce file browser.
    """
    query = u''
    try:
        page_num = int(request.GET.get('page', 1))
    except:
        page_num = 1

    form = FileSearchMinForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data.get('q', '')
    #filters = get_query_filters(request.user, 'files.view_file')
    files = File.objects.all()
    if not request.user.is_superuser:
        #  non-admin: show only those images uploaded by this user
        files = files.filter(Q(creator=request.user) | Q(owner=request.user))
    files = files.order_by('-create_dt')
    type = request.GET.get('type', '')
    if type == 'image':
        files = files.filter(f_type='image')
    elif type == 'media':
        files = files.filter(f_type='video')
    if query:
        files = files.filter(Q(file__icontains=query)|
                             Q(name__icontains=query))
    paginator = Paginator(files, 10)
    files = paginator.page(page_num)

    return render_to_resp(
        request=request, template_name=template_name, context={
            "files": files,
            'q': query,
            'page_num': page_num,
            'page_range': paginator.page_range,
            'csrf_token': csrf_get_token(request),
            'can_upload_file': has_perm(request.user, 'files.add_file')
        })


@csrf_exempt
@login_required
def tinymce_get_files(request):
    if request.is_ajax() and request.method == "POST":
        all_files = File.objects.order_by('-create_dt')
        paginator = Paginator(all_files, 10)
        page_num = request.POST.get('page_num', '')
        try:
            files = paginator.page(page_num)
        except Exception:
            return JSONResponse({'content': ''})

        return_string = ''
        for file_item in files:
            return_string += render_to_string(template_name='files/templates/tinymce_gallery.html', context={'file': file_item})

        return JSONResponse({'content': return_string})
    raise Http404


@login_required
def tinymce_upload_template(request, id, template_name="files/templates/tinymce_upload.html"):
    file = get_object_or_404(File, pk=id)
    return render_to_resp(
        request=request, template_name=template_name, context={
            'file': file
        })


@is_enabled('files')
@login_required
@admin_required
def report_most_viewed(request, form_class=MostViewedForm, template_name="files/reports/most_viewed.html"):
    """
    Displays a table of files sorted by views/downloads.
    """
    start_dt = date.today() + relativedelta(months=-2)
    end_dt = datetime.now()
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
        application='files', action='details', create_dt__range=(start_dt, end_dt))

    if file_type != 'all':
        event_logs = event_logs.filter(event_data__icontains=file_type)

    event_logs = event_logs.annotate(count=Count('object_id')).order_by('-count')

    EventLog.objects.log()

    return render_to_resp(
        request=request, template_name=template_name, context={
            'form': form,
            'event_logs': event_logs
        })


def display_less(request, path):
    """
    Display the .less files
    """
    content = ''
    if path:
        full_path = '%s/%s.less' % (settings.S3_SITE_ROOT_URL, path)
        url_obj = urlopen(full_path)
        content = url_obj.read()
    return HttpResponse(content, content_type="text/css")


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
                return HttpResponse(content, content_type=content_type)
        else:
            url = '%s/%s' % (settings.THEMES_DIR, path)
        return HttpResponseRedirect(url)
    raise Http404


class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self, obj='', json_opts={}, content_type="application/json", *args, **kwargs):
        content = simplejson.dumps(obj, **json_opts)
        super(JSONResponse, self).__init__(content, content_type, *args, **kwargs)


@csrf_exempt
def get_categories(request):
    if request.is_ajax() and request.method == "POST":
        main_category = request.POST.get('category', None)
        if main_category:
            sub_categories = FilesCategory.objects.filter(parent=main_category)
            count = sub_categories.count()
            sub_categories = list(sub_categories.values_list('pk','name'))
            data = json.dumps({"error": False,
                               "sub_categories": sub_categories,
                               "count": count})
        else:
            data = json.dumps({"error": True})

        return HttpResponse(data, content_type="text/plain")
    raise Http404
