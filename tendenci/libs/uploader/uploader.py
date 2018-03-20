# To use the uploader, make sure 'tendenci.libs.uploader' is listed in INSTALLED_APPS in
# settings.py, update your template as described in the comments in templatetags/uploader.py to
# render the uploader UI in the page, and define a Django view and associated callback functions to
# handle the uploads on the server.
#
# The Django view should look something like:
# def upload(request, *args, **kwargs):
#   from tendenci.libs.uploader import uploader
#   if request.method == 'POST':
#     return uploader.post(request, my_upload_handler)
# uploader.post() will handle all of the necessary interaction with the browser, will temporarily
# save each uploaded file in an "uploads" directory on the server, will call the specified callback
# function ("my_upload_handler"), then will delete the temporary file from the server.  The callback
# function must accept "file_path" and "uuid" keyword arguments, where the "file_path" argument will
# contain the path/name of the uploaded file, and the "uuid" argument will contain an identifier
# that may optionally be used for file deletion.  The callback function should process the uploaded
# file and (if necessary) move or copy the file to another location on the server for permanent
# storage.
#
# To support file deletion, update the configuration in your template to enable file deletion in the
# Fine Uploader UI, then add something like the following to the Django view:
#   elif request.method == 'DELETE':
#     return uploader.delete(request, my_delete_handler, args, kwargs)
# uploader.delete() will handle all of the necessary interaction with the browser and will call the
# specified callback function ("my_delete_handler").  The callback function must accept a "uuid"
# keyword argument which will contain the "uuid" of the file which should be deleted.

import os
import shutil
import json

from django.conf import settings

from .fine_uploader import utils
from .fine_uploader.views import make_response
from .fine_uploader.forms import UploadFileForm

settings.UPLOAD_DIRECTORY = os.path.join(settings.MEDIA_ROOT, 'uploads')

class CallbackError(Exception):
    pass

# These functions are based on the functions in fine_uploader/views.py but are modified to use
# callback functions to process uploaded files and deletion requests.

def post(request, callback):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        file_attrs = form.cleaned_data
        dest_path = os.path.join(settings.UPLOAD_DIRECTORY, file_attrs['qquuid'])
        dest_file = os.path.join(dest_path, file_attrs['qqfilename'])
        chunk = False
        if file_attrs['qqtotalparts'] is not None and int(file_attrs['qqtotalparts']) > 1:
            dest_file = os.path.join(dest_file+'.chunks', str(file_attrs['qqpartindex']))
            chunk = True

        utils.save_upload(file_attrs['qqfile'], dest_file)

        if chunk and (file_attrs['qqtotalparts'] - 1 == file_attrs['qqpartindex']):
            dest_file = os.path.join(dest_path, file_attrs['qqfilename'])
            utils.combine_chunks(file_attrs['qqtotalparts'], file_attrs['qqtotalfilesize'],
                source_folder=dest_file+'.chunks', dest=dest_file)
            shutil.rmtree(dest_file+'.chunks')
            chunk = False

        if not chunk:
            try:
                callback(file_path=dest_file, uuid=file_attrs['qquuid'])
            except CallbackError as e:
                return make_response(status=400,
                    content=json.dumps({
                        'success': False,
                        'error': '%s' % repr(e)
                    }))
            except Exception as e:
                return make_response(status=500,
                    content=json.dumps({
                        'success': False,
                        'error': 'Exception thrown by callback'
                    }))
            finally:
                shutil.rmtree(dest_path)

        return make_response(content=json.dumps({ 'success': True }))
    else:
        return make_response(status=400,
            content=json.dumps({
                'success': False,
                'error': '%s' % repr(form.errors)
            }))

def delete(request, callback, *args, **kwargs):
    uuid = kwargs.get('qquuid', '')
    if uuid:
        try:
            callback(uuid=uuid)
        except CallbackError as e:
            return make_response(status=400,
                content=json.dumps({
                    'success': False,
                    'error': '%s' % repr(e)
                }))
        except Exception as e:
            return make_response(status=500,
                content=json.dumps({
                    'success': False,
                    'error': 'Exception thrown by callback'
                }))
        return make_response(content=json.dumps({ 'success': True }))
    return make_response(status=404,
        content=json.dumps({
            'success': False,
            'error': 'File not present'
        }))
