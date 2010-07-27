from django.core.urlresolvers import resolve

class RedirectMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response # No need to check for a redirect for non-404 responses.
        
        path = request.get_full_path()
        try:
            redirect, args, kwargs = resolve(path, urlconf='redirects.dynamic_urls')
            args = [value for value in kwargs.values()]
            return redirect(request, *args)
        except:
            # No redirect was found. Return the response.
            return response
