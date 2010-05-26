from django.http import HttpResponseForbidden
from django.template import loader

class Http403(Exception):
    pass

def render_to_403(*args, **kwargs):
    """
    Returns a HttpResponseForbidden whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    response = None
    
    if not isinstance(args,list):
        args = []
        args.append('403.html')
        
    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    
    try:
        response = HttpResponseForbidden(loader.render_to_string(*args, **kwargs), **httpresponse_kwargs)
    except:
        raise Http403
        
    return response
        