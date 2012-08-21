"""This middleware takes the session identifier in a POST message and adds it to the cookies instead.

This is necessary because SWFUpload won't send proper cookies back; instead, all the cookies are
added to the form that gets POST-ed back to us.
"""

from django.conf import settings
from django.core.urlresolvers import reverse

class SWFUploadMiddleware(object):
    def process_request(self, request):
        swf_cookie_name = settings.SWFUPLOAD_COOKIE_NAME
        if request.method == 'POST':
            if request.POST.has_key("photoset_id"):
                photoset_id = int(request.POST["photoset_id"])
                if (request.path == reverse('photos_batch_add', args=[photoset_id])) and \
                        request.POST.has_key(swf_cookie_name):
                    
                    request.COOKIES[settings.SESSION_COOKIE_NAME] = request.POST[swf_cookie_name]
                if request.POST.has_key('csrftoken'):           
                    request.COOKIES["csrftoken"] = request.POST['csrftoken']

class MediaUploadMiddleware(object):
    def process_request(self, request):
        swf_cookie_name = settings.SWFUPLOAD_COOKIE_NAME
        
        if (request.method == 'POST') and (request.path == reverse('file.swfupload')) and \
                request.POST.has_key(swf_cookie_name):
            request.COOKIES[settings.SESSION_COOKIE_NAME] = request.POST[swf_cookie_name]
            
        if request.POST.has_key('csrftoken'):           
            request.COOKIES["csrftoken"] = request.POST['csrftoken']
            
    def process_response(self, request, response):
        # set cookie for swfupload
        if request.COOKIES.has_key(settings.SESSION_COOKIE_NAME):
            response.set_cookie(settings.SWFUPLOAD_COOKIE_NAME,
                                request.COOKIES[settings.SESSION_COOKIE_NAME])
        return response
