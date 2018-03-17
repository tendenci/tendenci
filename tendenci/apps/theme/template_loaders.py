"""
Wrapper for loading template based on a selected Theme.
"""
import os

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loaders.base import Loader

from django.utils._os import safe_join
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import SuspiciousFileOperation

from tendenci.libs.boto_s3.utils import read_theme_file_from_s3
from tendenci.apps.theme.utils import get_theme_root
from tendenci.apps.theme.middleware import get_current_request


class Loader(Loader):
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

    def __init__(self, engine, *args, **kwargs):
        """
        Hold the theme_root in self.theme_root instead of calling get_theme_root()
        in get_template_sources(). This significantly reduces the number of queries
        for get_setting('module', 'theme_editor', 'theme').
        (reduced # of queries from 3316 to 233 when testing on my local for an
        article view. - @jennyq)
        """
        self.theme_root = get_theme_root()
        super(Loader, self).__init__(engine)

    def get_template_sources(self, template_name, template_dirs=None):
        """Return the absolute paths to "template_name", when appended to the
        selected theme directory in THEMES_DIR.
        Any paths that don't lie inside one of the
        template dirs are excluded from the result set, for security reasons.
        """
        theme_templates = []
        current_request = get_current_request()
        # this is needed when the theme is changed
        self.theme_root = get_theme_root()
        if current_request and current_request.mobile:
            theme_templates.append(os.path.join(self.theme_root, 'mobile'))
        theme_templates.append(os.path.join(self.theme_root, 'templates'))

        for template_path in theme_templates:
            try:
                if settings.USE_S3_THEME:
                    yield os.path.join(template_path, template_name)
                else:
                    yield safe_join(template_path, template_name)
            except SuspiciousFileOperation:
                # The joined path was located outside of this particular
                # template_dir (it might be inside another one, so this isn't
                # fatal).
                pass

    def load_template_source(self, template_name, template_dirs=None):
        tried = []

        for filepath in self.get_template_sources(template_name, template_dirs):
            # First try to read from S3
            if settings.USE_S3_THEME:
                # first try to read from cache
                cache_key = ".".join([settings.SITE_CACHE_KEY, "theme", filepath])
                cached_template = cache.get(cache_key)
                if cached_template == "tried":
                    # Skip out of this on to the next template file
                    continue
                if cached_template:
                    return (cached_template, filepath)

                try:
                    file = read_theme_file_from_s3(filepath)
                    try:
                        cache.set(cache_key, file)
                        cache_group_key = "%s.theme_files_cache_list" % settings.SITE_CACHE_KEY
                        cache_group_list = cache.get(cache_group_key)

                        if cache_group_list is None:
                            cache.set(cache_group_key, [cache_key])
                        else:
                            cache_group_list += [cache_key]
                            cache.set(cache_group_key, cache_group_list)

                        return (file, filepath)
                    finally:
                        pass
                except:
                    # Cache that we tried this file
                    cache.set(cache_key, "tried")

            # Otherwise, look on to local file system.
            else:
                #print filepath
                try:
                    file = open(filepath)
                    try:
                        return (file.read(), filepath)
                    finally:
                        file.close()
                except IOError:
                    tried.append(filepath)
        if tried:
            error_msg = "Tried %s" % tried
        else:
            error_msg = "Your TEMPLATE_DIRS setting is empty. Change it to point to at least one template directory."
        raise TemplateDoesNotExist(_(error_msg))
    load_template_source.is_usable = True
