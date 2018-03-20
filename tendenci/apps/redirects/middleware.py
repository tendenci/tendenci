from django.urls import resolve
from django.utils.http import urlquote
from django.utils.deprecation import MiddlewareMixin


class RedirectMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        """ search url in redirects for 404 or 302 custom redirect """
        if response.status_code != 404 and (not (response.status_code == 302 and
                                           getattr(response, 'custom_redirect', False))):
            return response  # No need to check for a redirect for non-404 responses.
        # use urlquote so we can support '?' in the redirect
        path = urlquote(request.get_full_path())
        from tendenci.apps.handler404.models import Report404
        try:
            view, args, kwargs = resolve(path, urlconf='tendenci.apps.redirects.dynamic_urls')
            kwargs['request'] = request
            try:
                return view(*args, **kwargs)
            except:
                raise
        except Exception:
            # No redirect was found. Return the response.
            # Log the 404
            # print("e: ", e)
            report_list = Report404.objects.filter(url=path)[:1]
            if report_list:
                report = report_list[0]
                report.count = report.count + 1
            else:
                # Truncate to only get the first 200 characters
                report = Report404(url=path[:200])
            report.save()
            return response
