import os, mimetypes

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseServerError
from django.core.urlresolvers import reverse

import simplejson as json
from base.http import render_to_403
from files.models import File
from files.forms import FileForm
from perms.models import ObjectPermission

def index(request, id=None, download='', template_name="files/view.html"):
    if not id: return HttpResponseRedirect(reverse('file.search'))
    file = get_object_or_404(File, pk=id)

    # check permission
    if not request.user.has_perm('files.view_file', file):
        return render_to_403()

    try: data = file.file.read()
    except: raise Http404

    types = { # list of uncommon mimetypes
        'application/msword': ('.doc','.docx'),
        'application/ms-powerpoint': ('.ppt','.pptx'),
        'application/ms-excel': ('.xls','.xlsx'),
        'video/x-ms-wmv': ('.wmv',),
    }

    # add mimetypes
    for type in types:
        for ext in types[type]:
            mimetypes.add_type(type, ext)

    mimetype = mimetypes.guess_type(file.file.name)[0]
    response = HttpResponse(data, mimetype=mimetype)

    if download: download = 'attachment;'
    response['Content-Disposition'] = '%s filename=%s'% (download, file.file.name)

    if mimetype: return response
    else: raise Http404

def search(request, template_name="files/search.html"):
    files = File.objects.all().order_by('-create_dt')
    return render_to_response(template_name, {'files':files}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="files/print-view.html"):
    file = get_object_or_404(File, pk=id)

    # check permission
    if not request.user.has_perm('files.view_file', file):
        return render_to_403()

    return render_to_response(template_name, {'file': file}, 
        context_instance=RequestContext(request))
    
@login_required
def edit(request, id, form_class=FileForm, template_name="files/edit.html"):
    file = get_object_or_404(File, pk=id)

    # check permission
    if not request.user.has_perm('files.change_file', file):  
        return render_to_403()

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=file)
        if form.is_valid():
            file = form.save(commit=False)
            file.save()
    
            # remove all permissions on the object
            ObjectPermission.objects.remove_all(file)
            
            # assign new permissions
            user_perms = form.cleaned_data['user_perms']
            if user_perms:
                ObjectPermission.objects.assign(user_perms, file)               
    
            # assign creator permissions
            ObjectPermission.objects.assign(file.creator, file) 
                                                          
            return HttpResponseRedirect(reverse('file', args=[file.pk]))             
    else:
        form = form_class(request.user, instance=file)
    
    return render_to_response(template_name, {'file': file, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def add(request, form_class=FileForm, template_name="files/add.html"):

    # check permission
    if not request.user.has_perm('files.add_file'):  
        return render_to_403()

    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            
            # set up the user information
            file.creator = request.user
            file.creator_username = request.user.username
            file.owner = request.user
            file.owner_username = request.user.username
            
            file.save()

            # assign permissions for selected users
            user_perms = form.cleaned_data['user_perms']
            if user_perms: ObjectPermission.objects.assign(user_perms, file)
            
            # assign creator permissions
            ObjectPermission.objects.assign(file.creator, file) 
            
            return HttpResponseRedirect(reverse('file', args=[file.pk]))
    else:
        form = form_class(request.user)
       
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
    
@login_required
def delete(request, id, template_name="files/delete.html"):
    file = get_object_or_404(File, pk=id)

    # check permission
    if not request.user.has_perm('files.delete_file'): 
        return render_to_403()

    if request.method == "POST":
        file.delete()
        return HttpResponseRedirect(reverse('file.search'))

    return render_to_response(template_name, {'file': file}, 
        context_instance=RequestContext(request))


@login_required
def tinymce(request, template_name="media-files/tinymce.html"):
    """
        TinyMCE Insert/Edit images [Window]
        Passes in a list of files associated w/ "this" object
        Examples of "this": Articles, Pages, Releases module
    """
    from django.contrib.contenttypes.models import ContentType
    params = {'app_label': 0, 'model': 0, 'instance_id':0}
    files = File.objects.none() # EmptyQuerySet

    # if all required parameters are in the GET.keys() list
    # difference of 0, negated = True;
    if not set(params.keys()) - set(request.GET.keys()):        
        for item in params: params[item] = request.GET[item]
        try: # get content type
            contenttype = ContentType.objects.get(app_label=params['app_label'], model=params['model'])

            if params['instance_id'] == 'undefined':
                params['instance_id'] = 0

            files = File.objects.filter(content_type=contenttype, object_id=params['instance_id'])

            for media_file in files:
                file, ext = os.path.splitext(media_file.file.url)
                media_file.file.url_thumbnail = '%s_thumbnail%s' % (file, ext)
                media_file.file.url_medium = '%s_medium%s' % (file, ext)
                media_file.file.url_large = '%s_large%s' % (file, ext)
        except ContentType.DoesNotExist: raise Http404

    return render_to_response(template_name, {"media": files}, context_instance=RequestContext(request))


def swfupload(request):
    from django.contrib.contenttypes.models import ContentType
    import re

    if request.method == "POST":

        for file in request.FILES:
            uploaded_file = request.FILES[file]

            # use file to get create title
            clean_filename = os.path.splitext(uploaded_file.name)[0]

            # get POST data
            app_label = request.POST['storme_app_label']
            model = unicode(request.POST['storme_model']).lower()
            app_instance_id = request.POST['storme_instance_id']

            # update POST dict
            request.POST.update({'name': clean_filename, })
            request.POST.update({'user_id': 3, })
            request.POST.update({'application_id': 3, })
            request.POST.update({'app_instance_id': 123, })

        form = FileForm(request.POST, request.FILES)

        if form.is_valid():
            
            app_label = request.POST['storme_app_label']
            model = unicode(request.POST['storme_model']).lower()

            try: media_file = form.save(commit=False)
            except:
                import traceback
                traceback.print_exc()

            try: 
                media_file.name = re.sub(r'[^a-zA-Z0-9._]+', '-', request.FILES['file'].name)
                media_file.user = request.user
                media_file.application = ContentType.objects.get(app_label=app_label, model=model)
                media_file.application_instance_id = app_instance_id
                media_file.owner_id = 1
                media_file.creator_id = 1
                media_file.save()

                url_file, url_ext = os.path.splitext(media_file.file.url)
                url_thumbnail = (url_file + '_thumbnail' + url_ext)
                url_medium = (url_file + '_medium' + url_ext)
                url_large = (url_file + '_large' + url_ext)
    
    
    
#                media_file.copy_image([75, 75], hook='_thumbnail', crop=True)
#                media_file.copy_image([240, 240], hook='_medium')
#                media_file.copy_image([500, 500], hook='_large')
    
                d = {
                    "id" : media_file.id,
                    "name" : media_file.name,
                    "url" : media_file.file.url,
                    "url_thumbnail" : url_thumbnail,
                    "url_medium" : url_medium,
                    "url_large" : url_large            
                }
    
                print json.dumps([d])

            except: 
                import traceback
                traceback.print_exc()

            return HttpResponse(json.dumps([d]), mimetype="text/plain")
        else:
            return HttpResponseServerError(str(form._errors), mimetype="text/plain")

    else: # if not POST
        return HttpResponse("not good", mimetype="text/plain")
