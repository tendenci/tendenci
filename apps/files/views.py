import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.middleware.csrf import get_token as csrf_get_token

import simplejson as json
from base.http import Http403
from site_settings.utils import get_setting
from files.models import File
from files.utils import get_image
from files.forms import FileForm, MostViewedForm
from perms.decorators import admin_required
from perms.object_perms import ObjectPermission
from perms.utils import update_perms_and_save, has_perm, has_view_perm, get_query_filters
from event_logs.models import EventLog
from files.cache import FILE_IMAGE_PRE_KEY


def details(request, id=None, size=None, crop=False, quality=90, download=False, template_name="files/details.html"):
    from files.search_indexes import FileIndex
    if not id: return HttpResponseRedirect(reverse('file.search'))

    # if string and digit convert to integer
    if isinstance(quality, unicode) and quality.isdigit():
        quality = int(quality)

    file = get_object_or_404(File, pk=id)
    if not has_view_perm(request.user, 'files.view_file', file):
        raise Http403

    # check 'if public'
    if not file.is_public:
        if not request.user.is_authenticated():
            raise Http403

    # we either have the name in our database
    # or we pull the name straight off of the file
    file_name = file.name or file.file.name

    # get image binary
    try:
        data = file.file.read()
        file.file.close()
    except:
        raise Http404

    # log downloads and views
    if download:
        # if filew download
        attachment = 'attachment;'
        log_defaults = {
            'event_id' : 185000,
            'event_data': '%s %s (%d) dowloaded by %s' % (file.type(), file._meta.object_name, file.pk, request.user),
            'description': '%s downloaded' % file._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': file,
        }
        EventLog.objects.log(**log_defaults)
    else:
        attachment = ''

        if file.type() != 'image':

            # log file view
            EventLog.objects.log(**{
                'event_id' : 186000,
                'event_data': '%s %s (%d) viewed by %s' % (file.type(), file._meta.object_name, file.pk, request.user),
                'description': '%s viewed' % file._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': file,
            })

    # update index
    if file.type() != 'image':
        file_index = FileIndex(File)
        file_index.update_object(file)

    # if image size specified
    if file.type()=='image' and size:  # if size specified
        size= [int(s) for s in size.split('x')]  # convert to list
        # gets resized image from cache or rebuilds
        image = get_image(file.file, size, FILE_IMAGE_PRE_KEY, cache=True, unique_key=None)
        image = get_image(file.file, size, FILE_IMAGE_PRE_KEY, cache=True, crop=crop, quality=quality, unique_key=None)
        response = HttpResponse(mimetype='image/jpeg')
        response['Content-Disposition'] = '%s filename=%s'% (attachment, file_name)
        image.save(response, "JPEG", quality=quality)

        return response

    # set mimetype
    if file.mime_type():
        response = HttpResponse(data, mimetype=file.mime_type())
    else: raise Http404

    # return response
    response['Content-Disposition'] = '%s filename=%s'% (attachment, file_name)
    return response

def search(request, template_name="files/list.html"):
    """
    This page lists out all files from newest to oldest.
    If a search index is available, this page will also
    have the option to search through files.
    """
    has_index = get_setting('site', 'global', 'searchindex')
    query = request.GET.get('q', None)

    if has_index and query:
        files = File.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'files.view_file')
        files = File.objects.filter(filters).distinct()
        if request.user.is_authenticated():
            files = files.select_related()
    files = files.order_by('-update_dt')

    return render_to_response(template_name, {'files':files}, 
        context_instance=RequestContext(request))

def search_redirect(request):
    return HttpResponseRedirect(reverse('files'))

def print_view(request, id, template_name="files/print-view.html"):
    file = get_object_or_404(File, pk=id)

    # check permission
    if not has_view_perm(request.user,'files.view_file',file):
        raise Http403

    return render_to_response(template_name, {'file': file}, 
        context_instance=RequestContext(request))
    
@login_required
def edit(request, id, form_class=FileForm, template_name="files/edit.html"):
    file = get_object_or_404(File, pk=id)

    # check permission
    if not has_perm(request.user,'files.change_file',file):  
        raise Http403

    if request.method == "POST":

        form = form_class(request.POST, request.FILES, instance=file, user=request.user)

        if form.is_valid():
            file = form.save(commit=False)

            # update all permissions and save the model
            file = update_perms_and_save(request, form, file)

            log_defaults = {
                'event_id' : 182000,
                'event_data': '%s (%d) edited by %s' % (file._meta.object_name, file.pk, request.user),
                'description': '%s edited' % file._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': file,
            }
            EventLog.objects.log(**log_defaults)

            return HttpResponseRedirect(reverse('file.search'))
    else:
        form = form_class(instance=file, user=request.user)

    return render_to_response(template_name, {'file': file, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def add(request, form_class=FileForm, template_name="files/add.html"):

    # check permission
    if not has_perm(request.user,'files.add_file'):  
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

            log_defaults = {
                'event_id' : 181000,
                'event_data': '%s (%d) added by %s' % (file._meta.object_name, file.pk, request.user),
                'description': '%s added' % file._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': file,
            }
            EventLog.objects.log(**log_defaults)
            
            # assign creator permissions
            ObjectPermission.objects.assign(file.creator, file) 
            
            return HttpResponseRedirect(reverse('file.search'))
    else:
        form = form_class(user=request.user)
       
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
    
@login_required
def delete(request, id, template_name="files/delete.html"):
    file = get_object_or_404(File, pk=id)

    # check permission
    if not has_perm(request.user,'files.delete_file'): 
        raise Http403

    if request.method == "POST":
        log_defaults = {
            'event_id' : 183000,
            'event_data': '%s (%d) deleted by %s' % (file._meta.object_name, file.pk, request.user),
            'description': '%s deleted' % file._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': file,
        }
        EventLog.objects.log(**log_defaults)

        file.delete()

        if 'ajax' in request.POST:
            return HttpResponse('Ok')
        else:
            return HttpResponseRedirect(reverse('file.search'))
        

    return render_to_response(template_name, {'file': file}, 
        context_instance=RequestContext(request))


@login_required
def tinymce(request, template_name="files/templates/tinymce.html"):
    """
    TinyMCE Insert/Edit images [Window]
    Passes in a list of files associated w/ "this" object
    Examples of "this": Articles, Pages, Releases module
    """
    from django.contrib.contenttypes.models import ContentType
    params = {'app_label': 0, 'model': 0, 'instance_id':0}
    files = File.objects.none() # EmptyQuerySet

    # if all required parameters are in the GET.keys() list
    if not set(params.keys()) - set(request.GET.keys()):        

        for item in params:
            params[item] = request.GET[item]

        try: # get content type
            contenttype = ContentType.objects.get(app_label=params['app_label'], model=params['model'])

            instance_id = params['instance_id']
            if instance_id == 'undefined':
                instance_id = 0

            files = File.objects.filter(
                content_type=contenttype, 
                object_id=instance_id)

            for media_file in files:
                file, ext = os.path.splitext(media_file.file.url)
                media_file.file.url_thumbnail = '%s_thumbnail%s' % (file, ext)
                media_file.file.url_medium = '%s_medium%s' % (file, ext)
                media_file.file.url_large = '%s_large%s' % (file, ext)
        except ContentType.DoesNotExist: raise Http404

    return render_to_response(template_name, {
        "media": files, 
        'csrf_token':csrf_get_token(request),
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

        form = FileForm(request.POST, request.FILES, user=request.user)

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
            file.allow_anonymous_view = True
            file.save()
        except Exception, e:
            print e

        d = {
            "id" : file.id,
            "name" : file.name,
            "url" : file.file.url,
        }

        return HttpResponse(json.dumps([d]), mimetype="text/plain")

@login_required
def tinymce_upload_template(request, id, template_name="files/templates/tinymce_upload.html"):
    file = get_object_or_404(File, pk=id)
    return render_to_response(template_name, {'file': file}, 
        context_instance=RequestContext(request))

@login_required
@admin_required
def report_most_viewed(request, form_class=MostViewedForm, template_name="files/reports/most_viewed.html"):
    """
    Displays a table of files sorted by views/downloads.
    """
    from django.db.models import Count
    from datetime import date
    from datetime import timedelta
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
        event_id__in=(185000,186000), create_dt__range=(start_dt, end_dt))

    if file_type != 'all':
        event_logs = event_logs.filter(event_data__icontains=file_type)

    event_logs =event_logs.annotate(count=Count('object_id'))

    return render_to_response(template_name, {
        'form': form,
        'event_logs':event_logs
        }, context_instance=RequestContext(request))

