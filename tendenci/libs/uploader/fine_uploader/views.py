import json
import logging
import os
import os.path
import shutil

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp

from .forms import UploadFileForm
from . import utils

logger = logging.getLogger('django')


##
# Utils
##
def make_response(status=200, content_type='text/plain', content=None):
    """ Construct a response to an upload request.
    Success is indicated by a status of 200 and { "success": true }
    contained in the content.

    Also, content-type is text/plain by default since IE9 and below chokes
    on application/json. For CORS environments and IE9 and below, the
    content-type needs to be text/html.
    """
    response = HttpResponse()
    response.status_code = status
    response['Content-Type'] = content_type
    response.content = content
    return response


##
# Views
##
def home(request):
    """ The 'home' page. Returns an HTML page with Fine Uploader code
    ready to upload. This HTML page should contain your client-side code
    for instatiating and modifying Fine Uploader.
    """
    return render_to_resp(request=request, template_name='fine_uploader/index.html')


class UploadView(View):
    """ View which will handle all upload requests sent by Fine Uploader.
    See: https://docs.djangoproject.com/en/dev/topics/security/#user-uploaded-content-security

    Handles POST and DELETE requests.
    """

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(UploadView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """A POST request. Validate the form and then handle the upload
        based ont the POSTed data. Does not handle extra parameters yet.
        """
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_upload(request.FILES['qqfile'], form.cleaned_data)
            return make_response(content=json.dumps({ 'success': True }))
        else:
            return make_response(status=400,
                content=json.dumps({
                    'success': False,
                    'error': '%s' % repr(form.errors)
                }))

    def delete(self, request, *args, **kwargs):
        """A DELETE request. If found, deletes a file with the corresponding
        UUID from the server's filesystem.
        """
        qquuid = kwargs.get('qquuid', '')
        if qquuid:
            try:
                handle_deleted_file(qquuid)
                return make_response(content=json.dumps({ 'success': True }))
            except Exception as e:
                return make_response(status=400,
                    content=json.dumps({
                        'success': False,
                        'error': '%s' % repr(e)
                    }))
        return make_response(status=404,
            content=json.dumps({
                'success': False,
                'error': 'File not present'
            }))

def handle_upload(f, fileattrs):
    """ Handle a chunked or non-chunked upload.
    """
    logger.info(fileattrs)

    chunked = False
    dest_folder = os.path.join(settings.UPLOAD_DIRECTORY, fileattrs['qquuid'])
    dest = os.path.join(dest_folder, fileattrs['qqfilename'])

    # Chunked
    if int(fileattrs['qqtotalparts']) > 1:
        chunked = True
        dest_folder = os.path.join(settings.CHUNKS_DIRECTORY, fileattrs['qquuid'])
        dest = os.path.join(dest_folder, fileattrs['qqfilename'], str(fileattrs['qqpartindex']))
        logger.info('Chunked upload received')

    utils.save_upload(f, dest)
    logger.info('Upload saved: %s' % dest)

    # If the last chunk has been sent, combine the parts.
    if chunked and (fileattrs['qqtotalparts'] - 1 == fileattrs['qqpartindex']):

        logger.info('Combining chunks: %s' % os.path.dirname(dest))
        utils.combine_chunks(fileattrs['qqtotalparts'],
            fileattrs['qqtotalfilesize'],
            source_folder=os.path.dirname(dest),
            dest=os.path.join(settings.UPLOAD_DIRECTORY, fileattrs['qquuid'], fileattrs['qqfilename']))
        logger.info('Combined: %s' % dest)

        shutil.rmtree(os.path.dirname(os.path.dirname(dest)))

def handle_deleted_file(uuid):
    """ Handles a filesystem delete based on UUID."""
    logger.info(uuid)

    loc = os.path.join(settings.UPLOAD_DIRECTORY, uuid)
    shutil.rmtree(loc)
