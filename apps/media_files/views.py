# python
from datetime import datetime

# django
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Template
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

# local
from media_files.models import MediaFile
from media_files.forms import MediaFileForm

def media_files(request, template_name="media-files/media-files.html"):
    #if request.user.is_authenticated():
    media = MediaFile.objects.order_by("-release_dt")
    return render_to_response(template_name, {"media": media}, context_instance=RequestContext(request))

@login_required
def media_file_upload(request):
    from django.contrib.contenttypes.models import ContentType
    import re

    if request.method == "POST":

        for file in request.FILES:
            uploaded_file = request.FILES[file]

            # use file to get create title
            clean_filename = uploaded_file.name[::-1].split(".", 1)[1][::-1] 

            # get POST data
            app_label = request.POST['storme_app_label']
            model = unicode(request.POST['storme_model']).lower()
            app_instance_id = request.POST['storme_instance_id']

            # update POST dict
            request.POST.update({'name': clean_filename, })
            request.POST.update({'user_id': 3, })
            request.POST.update({'application_id': 3, })
            request.POST.update({'app_instance_id': 123, })

        form = MediaFileForm(request.POST, request.FILES)
        if form.is_valid():
            
            app_label = request.POST['storme_app_label']
            model = unicode(request.POST['storme_model']).lower()

            media_file = form.save(commit=False)
            media_file.name = re.sub(r'[^a-zA-Z0-9._]+', '-', request.FILES['file'].name)
            media_file.user = request.user
            media_file.application = ContentType.objects.get(app_label=app_label, model=model)
            media_file.application_instance_id = app_instance_id
            media_file.save()

            import os
            import Image

            url_file, url_ext = os.path.splitext(media_file.file.url)
            url_thumbnail = (url_file + '_thumbnail' + url_ext)
            url_medium = (url_file + '_medium' + url_ext)
            url_large = (url_file + '_large' + url_ext)

            media_file.copy_image([75, 75], hook='_thumbnail', crop=True)
            media_file.copy_image([240, 240], hook='_medium')
            media_file.copy_image([500, 500], hook='_large')

            import simplejson as json
            d = {
                "id" : media_file.id,
                "name" : media_file.name,
                "url" : media_file.file.url,
                "url_thumbnail" : url_thumbnail,
                "url_medium" : url_medium,
                "url_large" : url_large            
            }

            return HttpResponse(json.dumps([d]), mimetype="text/plain")
        else:
            return HttpResponseServerError(str(form._errors), mimetype="text/plain")

    else:
        return HttpResponse("not good", mimetype="text/plain")

@login_required
def media_file_delete(request, id):

    try:
        media_file = MediaFile.objects.get(id=id)
        media_file.delete()
        return HttpResponse("good", mimetype="text/plain")
    except MediaFile.DoesNotExist:
        return HttpResponseServerError("not good", mimetype="text/plain")

@login_required
def media_file_tinymce(request, template_name="media-files/tinymce.html"):
    from django.contrib.contenttypes.models import ContentType
    from os.path import splitext
    params = {'app_label': 0, 'model': 0, 'instance_id':0}
    media = MediaFile.objects.none() # EmptyQuerySet

    # if all required parameters are in the GET.keys() list
    if not set(params.keys()) - set(request.GET.keys()):        
        for item in params: params[item] = request.GET[item]
        try: # get content type
            contenttype = ContentType.objects.get(app_label=params['app_label'], model=params['model'])
            media = MediaFile.objects.filter(application=contenttype, application_instance_id=params['instance_id'])

            for media_file in media:
                file, ext = splitext(media_file.file.url)
                media_file.file.url_thumbnail = file + '_thumbnail' + ext
                media_file.file.url_medium = file + '_medium' + ext
                media_file.file.url_large = file + '_large' + ext
        except ContentType.DoesNotExist: pass

    return render_to_response(template_name, {"media": media}, context_instance=RequestContext(request))

@login_required
def media_file_tinymce_proxy(request, template_name="media-files/tinymce-proxy.html"):
    from ATD import ATD

    try: key = request.POST["key"]
    except: key = ""
    try: data = request.POST["data"]
    except: data = ""
    
    ATD.setDefaultKey(key)
    response = ATD.checkDocumentXML(data)
    return HttpResponse(response, mimetype="text/plain")

@login_required
def media_file_template_image(request, template_name="media-files/image_template.html"):
    return render_to_response(template_name, context_instance=RequestContext(request))
    
    
    
    
