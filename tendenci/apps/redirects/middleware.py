from django.core.urlresolvers import resolve


class RedirectMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response  # No need to check for a redirect for non-404 responses.

        path = request.get_full_path()
        from tendenci.core.handler404.models import Report404
        try:
            redirect, args, kwargs = resolve(path, urlconf='tendenci.apps.redirects.dynamic_urls')
            args = [value for value in kwargs.values()]
            to_url = kwargs.pop('url')
            for key in kwargs.keys():
                to_url = to_url.replace("(%s)" % key, kwargs[key])
            args[0] = to_url
            return redirect(request, *args)
        except Exception, e:
            # No redirect was found. Return the response.
            # Log the 404
            report_list = Report404.objects.filter(url=path)[:1]
            if report_list:
                report = report_list[0]
                report.count = report.count + 1
            else:
                # Truncate to only get the first 200 characters
                report = Report404(url=path[:200])
            report.save()
            return response
