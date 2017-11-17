import sys

from django.http import HttpResponseForbidden, HttpResponseServerError
from django.template import loader
from django.http import HttpResponseRedirect


class HttpCustomResponseRedirect(HttpResponseRedirect):
    custom_redirect = True

class Http403(Exception):
    pass

def render_to_403(*args, **kwargs):
    """
    Returns a HttpResponseForbidden whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    if not isinstance(args,list):
        args = []
        args.append('403.html')

    httpresponse_kwargs = {'content_type': kwargs.pop('mimetype', None)}

    response = HttpResponseForbidden(loader.render_to_string(*args, **kwargs), **httpresponse_kwargs)

    return response

class MissingApp(Exception):
    pass

def render_to_missing_app(*args, **kwargs):
    if not isinstance(args,list):
        args = []
        args.append('base/missing_app.html')

    httpresponse_kwargs = {'content_type': kwargs.pop('mimetype', None)}

    value = sys.exc_info()[1]
    args.append({'exception_value': value})

    response = HttpResponseServerError(loader.render_to_string(*args, **kwargs), **httpresponse_kwargs)

    return response
