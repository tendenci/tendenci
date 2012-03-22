import os
from django.template import loader, TemplateDoesNotExist
from django.template.loader import get_template, Template
from django.http import HttpResponse
from django.conf import settings

from theme.utils import get_theme_template
from theme.template_loaders import get_default_template

def themed_response(*args, **kwargs):
    """Returns a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    return HttpResponse(render_to_theme(*args, **kwargs), **httpresponse_kwargs)
    
def render_to_theme(template_name, dictionary=None, context_instance=None):
    """Loads the given template_name and renders it with the given dictionary as
    context. The template_name may be a string to load a single template using
    get_template, or it may be a tuple to use select_template to find one of
    the templates in the list. Returns a string.
    This shorcut prepends the template_name given with the selected theme's 
    directory
    """
    dictionary = dictionary or {}
    
    if context_instance:
        context_instance.update(dictionary)
    else:
        context_instance = Context(dictionary)
    
    toggle = context_instance["TOGGLE_TEMPLATE"]
    theme = context_instance['THEME']
    theme_template = get_theme_template(template_name, theme=theme)
    context_instance["THEME_TEMPLATE"] = template_name
    context_instance["CUSTOM_TEMPLATE"] = True
    
    #if 'homepage.html' in template_name:
    #    context_instance["CUSTOM_TEMPLATE"] = False
    
    if toggle=="TRUE":
        t = get_default_template(template_name)
    else:
        if isinstance(template_name, (list, tuple)):
            try:
                t = select_template(theme_template)
            except TemplateDoesNotExist:
                # load the default file
                t = get_default_template(template_name)
                context_instance["CUSTOM_TEMPLATE"] = False
        else:
            try:
                t = get_template(theme_template)
            except TemplateDoesNotExist:
                # load the default file
                t = get_default_template(template_name)
                context_instance["CUSTOM_TEMPLATE"] = False
    return t.render(context_instance)
