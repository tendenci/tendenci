"""This middleware takes the session identifier in a POST message and adds it to the cookies instead.

This is necessary because SWFUpload won't send proper cookies back; instead, all the cookies are
added to the form that gets POST-ed back to us.
"""
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect, get_host


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


class SSLRedirectMiddleware(object):
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'SSL' in view_kwargs:
            secure = view_kwargs['SSL']
            del view_kwargs['SSL']

            if not secure == self._is_secure(request):
                return self._redirect(request, secure)

    def _is_secure(self, request):
        if request.is_secure():
	        return True

        #Handle the Webfaction case until this gets resolved in the request.is_secure()
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

        return False

    def _redirect(self, request, secure):
        protocol = secure and "https" or "http"
        newurl = "%s://%s%s" % (protocol, get_host(request), request.get_full_path())

        return HttpResponsePermanentRedirect(newurl)
