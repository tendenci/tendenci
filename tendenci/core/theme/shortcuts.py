import re
from django.template import TemplateDoesNotExist, Context
from django.template.loader import find_template, find_template_loader, \
    get_template_from_string, select_template, make_origin
from django.http import HttpResponse
from django.conf import settings
from tendenci.core.theme.utils import get_theme_template, get_theme_root

non_theme_source_loaders = None


def find_default_template(name, dirs=None):
    """
    Exclude the theme.template_loader
    So we can properly get the templates not part of any theme.
    """
    # Calculate template_source_loaders the first time the function is executed
    # because putting this logic in the module-level namespace may cause
    # circular import errors. See Django ticket #1292.

    global non_theme_source_loaders
    if non_theme_source_loaders is None:
        loaders = []
        for loader_name in settings.TEMPLATE_LOADERS:
            if loader_name != 'theme.template_loaders.load_template_source':
                loader = find_template_loader(loader_name)
                if loader is not None:
                    loaders.append(loader)
        non_theme_source_loaders = tuple(loaders)
    for loader in non_theme_source_loaders[-1:]:
        try:
            source, display_name = loader(name, dirs)
            return (source, make_origin(display_name, loader, name, dirs))
        except TemplateDoesNotExist:
            pass
    raise TemplateDoesNotExist(name)


def get_default_template(template_name):
    """
    Returns a compiled Template object for the given template name,
    handling template inheritance recursively.
    """
    template, origin = find_default_template(template_name)

    if not hasattr(template, 'render'):
        # template needs to be compiled
        template = get_template_from_string(template, origin, template_name)
    return template


def get_template(template_name):
    """
    Returns a compiled Template object for the given template name,
    handling template inheritance recursively.
    Copy from django.template.loader modified to return "origin."
    """
    template, origin = find_template(template_name)
    if not hasattr(template, 'render'):
        # template needs to be compiled
        template = get_template_from_string(template, origin, template_name)
    return template, origin


def themed_response(*args, **kwargs):
    """Returns a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    return HttpResponse(render_to_theme(*args, **kwargs), **httpresponse_kwargs)


def strip_content_above_doctype(html):
    """Strips any content above the doctype declaration out of the
    resulting template. If no doctype declaration, it returns the input.

    This was done because content above the doctype in IE8 triggers the
    browser to go into quirks mode which can break modern HTML5 and CSS3
    elements from the theme.
    """
    try:
        doctype_position = html.index('<!D')
        html = html[doctype_position:]
    except ValueError:
        pass

    return html

def render_to_theme(template_name, dictionary={}, context_instance=Context):
    """Loads the given template_name and renders it with the given dictionary as
    context. The template_name may be a string to load a single template using
    get_template, or it may be a tuple to use select_template to find one of
    the templates in the list. Returns a string.
    This shorcut prepends the template_name given with the selected theme's
    directory
    """

    context_instance.update(dictionary)
    toggle = 'TOGGLE_TEMPLATE' in context_instance
    theme = context_instance['THEME']
    theme_template = get_theme_template(template_name, theme=theme)
    context_instance["THEME_TEMPLATE"] = template_name
    context_instance["CUSTOM_TEMPLATE"] = False

    if toggle:
        t = get_default_template(template_name)
    else:
        if isinstance(template_name, (list, tuple)):
            try:
                t = select_template(theme_template)
            except TemplateDoesNotExist:
                t = get_default_template(template_name)
                context_instance["CUSTOM_TEMPLATE"] = False
        else:
            try:
                t, origin = get_template(theme_template)
                if origin and re.search("^%s.+" % get_theme_root(), origin.name):
                    context_instance["CUSTOM_TEMPLATE"] = True

                if 'homepage.html' in template_name:
                    context_instance["CUSTOM_TEMPLATE"] = False

            except TemplateDoesNotExist:
                t = get_default_template(template_name)
                context_instance["CUSTOM_TEMPLATE"] = False

    return strip_content_above_doctype(t.render(context_instance))
