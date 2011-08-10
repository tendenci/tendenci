from django.template import loader, TemplateDoesNotExist
from django.template.loader import get_template
from django.http import HttpResponse

def themed_response(*args, **kwargs):
    """
    Returns a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    This shorcut prepends the template_name given with the selected theme's 
    directory
    """
    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    theme = kwargs['context_instance']['THEME']
    #convert args to list
    list_args = list(args)
    try: #check for a themed template
        template = get_template("%s/templates/%s"%(theme,args[0]))
    except TemplateDoesNotExist, e:
        print e
        template = None
    if template:
        list_args[0] = "%s/templates/%s"%(theme,args[0])
    return HttpResponse(loader.render_to_string(*list_args, **kwargs), **httpresponse_kwargs)
