import re

from django.http import HttpResponse
from django.template import TemplateDoesNotExist, engines
from django.template.loader import get_template, select_template
from django.template.base import Template as DjangoBackendTemplate
from django.template.backends.django import Template as DjangoLoaderTemplate, reraise
from django.template.loaders.cached import Loader as CachedLoader

from tendenci.apps.theme.template_loaders import Loader as ThemeLoader
from tendenci.apps.theme.utils import get_theme_root


# Based on find_template() in django/template/engine.py but modified to skip any
# Cached Loaders, to skip the Tendenci Theme Loader
def find_default_django_template(loaders, name):
    tried = []
    for loader in loaders:
        try:
            if isinstance(loader, ThemeLoader):
                continue
            if isinstance(loader, CachedLoader):
                # See django/template/loaders/cached.py
                template, origin = find_default_django_template(loader.loaders, name)
                return template, template.origin
            template = loader.get_template(name)
            return template, template.origin
        except TemplateDoesNotExist as e:
            tried.extend(e.tried)
    raise TemplateDoesNotExist(name, tried=tried)


# Based on get_django_template() in django/template/backends/django.py and
# django/template/engine.py but modified to override the find_template() call
def get_default_django_template(backend, template_name):
    engine = backend.engine
    try:
        template, origin = find_default_django_template(engine.template_loaders, template_name)
        if not hasattr(template, 'render'):
            template = DjangoBackendTemplate(template, origin, template_name, engine=engine)
        return DjangoLoaderTemplate(template, backend)
    except TemplateDoesNotExist as exc:
        reraise(exc, backend)


# Based on the original methods in django/template/loader.py but modified to
# override the 'django' engine
def get_default_template(template_name):
    chain = []
    for engine in engines.all():
        try:
            if engine.name == 'django':
                return get_default_django_template(engine, template_name)
            return engine.get_template(template_name)
        except TemplateDoesNotExist as e:
            chain.append(e)
    raise TemplateDoesNotExist(template_name, chain=chain)
def select_default_template(template_name_list):
    chain = []
    for template_name in template_name_list:
        for engine in engines.all():
            try:
                if engine.name == 'django':
                    return get_default_django_template(engine, template_name)
                return engine.get_template(template_name)
            except TemplateDoesNotExist as e:
                chain.append(e)
    if template_name_list:
        raise TemplateDoesNotExist(', '.join(template_name_list), chain=chain)
    else:
        raise TemplateDoesNotExist("No template names provided")


# This should be called instead of django.shortcuts.render() by using:
# from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
# instead of:
# from django.shortcuts import render as render_to_resp
# in all views
def themed_response(*args, **kwargs):
    """Returns a HttpResponse whose content is filled with the equivalent of the
    result of calling django.template.loader.render_to_string() with the passed
    arguments.
    """
    if 'content_type' in kwargs:
        content_type = kwargs.pop('content_type')
    elif 'mimetype' in kwargs:
        content_type = kwargs.pop('mimetype')
    else:
        content_type = None
    return HttpResponse(render_to_theme(*args, **kwargs), content_type=content_type)


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

def render_to_theme(request, template_name, context={}, **kwargs):
    """Loads the given template_name and renders it with the given context.
    The template_name may be a string to load a single template using
    get_template, or it may be a tuple to use select_template to find one of
    the templates in the list. Returns a string.
    This shorcut prepends the template_name given with the selected theme's
    directory
    """

    disable_theme = 'DISABLE_THEME' in context
    context['CUSTOM_THEME'] = False
    context['THEME_TEMPLATE'] = template_name

    if disable_theme:
        if isinstance(template_name, (list, tuple)):
            t = select_default_template(template_name)
        else:
            t = get_default_template(template_name)
    else:
        if isinstance(template_name, (list, tuple)):
            t = select_template(template_name)
        else:
            t = get_template(template_name)
        if t.origin and re.search(r'^%s.+' % get_theme_root(), t.origin.name):
            context['CUSTOM_THEME'] = True

    return strip_content_above_doctype(t.render(context=context, request=request))
