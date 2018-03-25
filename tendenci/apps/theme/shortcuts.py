from django.http import HttpResponse
from django.template import TemplateDoesNotExist, engines
from django.template.loader import get_template
from django.template.base import Template as DjangoBackendTemplate
from django.template.backends.django import Template as DjangoLoaderTemplate, reraise
from django.template.loaders.cached import Loader as CachedLoader

from tendenci.apps.theme.utils import get_theme_root


# Based on find_template() in django/template/engine.py but modified to skip any
# CachedLoaders
def find_django_template_without_cache(loaders, name):
    tried = []
    for loader in loaders:
        try:
            if isinstance(loader, CachedLoader):
                # CachedLoader.loaders is the list of loaders managed by the
                # CachedLoader (See django/template/loaders/cached.py)
                template, origin = find_django_template_without_cache(loader.loaders, name)
                return template, template.origin
            template = loader.get_template(name)
            return template, template.origin
        except TemplateDoesNotExist as e:
            tried.extend(e.tried)
    raise TemplateDoesNotExist(name, tried=tried)


# Based on get_template() in django/template/backends/django.py and
# django/template/engine.py but modified to override the find_template() call
def get_django_template_without_cache(backend, template_name):
    engine = backend.engine
    try:
        template, origin = find_django_template_without_cache(engine.template_loaders, template_name)
        if not hasattr(template, 'render'):
            template = DjangoBackendTemplate(template, origin, template_name, engine=engine)
        return DjangoLoaderTemplate(template, backend)
    except TemplateDoesNotExist as exc:
        reraise(exc, backend)


# Based on get_template() in django/template/loader.py and
# django/template/engine.py but modified to override the 'django' engine
def get_template_without_cache(template_name):
    chain = []
    for engine in engines.all():
        try:
            if engine.name == 'django':
                return get_django_template_without_cache(engine, template_name)
            return engine.get_template(template_name)
        except TemplateDoesNotExist as e:
            chain.append(e)
    raise TemplateDoesNotExist(template_name, chain=chain)


def _strip_content_above_doctype(html):
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


# Render a response with optional template caching and with some extra
# theme-related context.
def themed_response(request, template_name, context={}, **kwargs):
    """
    This should be called instead of django.shortcuts.render() in all views, by
    using:
    from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
    Instead of:
    from django.shortcuts import render as render_to_resp

    ``template_name`` may be a string to render a single template, or a tuple or
    list of strings to try each template in order and use the first that exists.

    Returns an HttpResponse equivalent to the one that would be returned by
    django.shortcuts.render() given the same arguments.
    """

    if (('theme' in request.GET or 'disable_cache' in request.GET or
        'enable_cache' in request.GET) and request.user.profile.is_superuser):

        if request.GET.get('theme'):
            request.session['theme'] = request.GET.get('theme')
        elif 'theme' in request.session:
            del request.session['theme']

        if 'disable_cache' in request.GET:
            request.session['explicit_disable_cache'] = True
        if 'enable_cache' in request.GET:
            if 'explicit_disable_cache' in request.session:
                del request.session['explicit_disable_cache']

        if ('theme' in request.session or
            'explicit_disable_cache' in request.session):
            request.session['disable_cache'] = True
        elif 'disable_cache' in request.session:
            del request.session['disable_cache']

    if isinstance(template_name, (list, tuple)):
        template_name_list = template_name
        if not template_name_list:
            raise TemplateDoesNotExist("No template names provided")
        template = None
        # Loosely based on select_template() in django/template/loader.py and
        # django/template/engine.py
        chain = []
        for template_name in template_name_list:
            try:
                if 'disable_cache' in request.session:
                    template = get_template_without_cache(template_name)
                else:
                    template = get_template(template_name)
            except TemplateDoesNotExist as e:
                chain += e.chain
        if template is None:
            raise TemplateDoesNotExist(', '.join(template_name_list), chain=chain)
    else:
        if 'disable_cache' in request.session:
            template = get_template_without_cache(template_name)
        else:
            template = get_template(template_name)

    context['TEMPLATE_NAME'] = template.origin.template_name
    template_path = template.origin.name
    context['TEMPLATE_FROM_CUSTOM_THEME'] = template_path.startswith(get_theme_root())

    context['CACHE_DISABLED'] = request.session.get('disable_cache', False)

    rendered = _strip_content_above_doctype(template.render(context=context, request=request))

    if 'content_type' in kwargs:
        content_type = kwargs.pop('content_type')
    elif 'mimetype' in kwargs:
        content_type = kwargs.pop('mimetype')
    else:
        content_type = None

    return HttpResponse(rendered, content_type=content_type)
