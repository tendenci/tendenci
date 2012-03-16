"""
Wrapper for loading template based on a selected Theme.
"""
import os

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import (BaseLoader, get_template_from_string,
    find_template_loader, make_origin)
from django.utils._os import safe_join
from theme.utils import get_theme_root

non_theme_source_loaders = None

class Loader(BaseLoader):
    """Loader that includes a theme's templates files that enables 
    template overriding similar to how a project's templates dir overrides
    an app's templates dir. In other words this takes advantage of django's
    template prioritization.
    Notes:
    This takes into account the ACTIVE THEME only.
    The other themes are still available but must be accessed in a 
    different manner. Look into theme's theme_tags.py and shorcuts.py
    Since the context is not available. We will be unable to mark if 
    a template is custom from here.
    """
    is_usable = True

    def get_template_sources(self, template_name, template_dirs=None):
        """Return the absolute paths to "template_name", when appended to the
        selected theme directory in THEMES_DIR.
        Any paths that don't lie inside one of the
        template dirs are excluded from the result set, for security reasons.
        """
        theme_templates = os.path.join(get_theme_root(), 'templates')
        try:
            yield safe_join(theme_templates, template_name)
        except UnicodeDecodeError:
            # The template dir name was a bytestring that wasn't valid UTF-8.
            raise
        except ValueError:
            # The joined path was located outside of this particular
            # template_dir (it might be inside another one, so this isn't
            # fatal).
            pass
    
    def load_template_source(self, template_name, template_dirs=None):
        tried = []
        for filepath in self.get_template_sources(template_name, template_dirs):
            try:
                file = open(filepath)
                try:
                    return (file.read().decode(settings.FILE_CHARSET), filepath)
                finally:
                    file.close()
            except IOError:
                tried.append(filepath)
        if tried:
            error_msg = "Tried %s" % tried
        else:
            error_msg = "Your TEMPLATE_DIRS setting is empty. Change it to point to at least one template directory."
        raise TemplateDoesNotExist(error_msg)
    load_template_source.is_usable = True

_loader = Loader()

def load_template_source(template_name, template_dirs=None):
    # For backwards compatibility
    return _loader.load_template_source(template_name, template_dirs)
load_template_source.is_usable = True

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
    for loader in non_theme_source_loaders:
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
