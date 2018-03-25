"""
Wrapper for loading template based on a selected Theme.
"""
import os
import errno

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.base import Origin
from django.template.loaders.base import Loader

from django.utils._os import safe_join
from django.core.cache import cache
from django.core.exceptions import SuspiciousFileOperation

from tendenci.apps.theme.utils import get_theme_root
from tendenci.apps.theme.middleware import get_current_request
from tendenci.libs.boto_s3.utils import read_theme_file_from_s3


class Loader(Loader):
    """Loader that includes a theme's templates files that enables
    template overriding similar to how a project's templates dir overrides
    an app's templates dir. In other words this takes advantage of django's
    template prioritization.
    """

    def __init__(self, engine, *args, **kwargs):
        # Hold the theme_root in self.theme_root instead of calling
        # get_theme_root() in get_template_sources(). This significantly reduces
        # the number of queries for
        # get_setting('module', 'theme_editor', 'theme').
        # (reduced # of queries from 3316 to 233 when testing on my local for an
        # article view. - @jennyq)
        # Reverted in daa0910b02 because it prevents theme changes without server
        # restart.
        #self.theme_root = get_theme_root()
        super(Loader, self).__init__(engine)

    def get_template_sources(self, template_name, template_dirs=None):
        """
        Return possible absolute paths to "template_name" in the current theme
        and any themes it inherits from.
        Any paths that don't lie inside one of the template dirs are excluded
        from the result set for security reasons.
        """
        theme_templates = []
        current_request = get_current_request()
        self.theme_root = get_theme_root()
        if current_request and current_request.mobile:
            theme_templates.append(os.path.join(self.theme_root, 'mobile'))
        theme_templates.append(os.path.join(self.theme_root, 'templates'))

        for template_path in theme_templates:
            try:
                if settings.USE_S3_THEME:
                    template_file = os.path.join(template_path, template_name)
                else:
                    template_file = safe_join(template_path, template_name)
                origin = Origin(name=template_file, template_name=template_name, loader=self)
                origin.template_from_theme = True
                yield origin
            except SuspiciousFileOperation:
                # The joined path was located outside of this particular
                # template_dir (it might be inside another one, so this isn't
                # fatal).
                pass

    def get_contents(self, origin):

        if settings.USE_S3_THEME:
            cache_key = ".".join([settings.SITE_CACHE_KEY, "theme", origin.name])

            cached_template = cache.get(cache_key)
            if cached_template == "tried":
                raise TemplateDoesNotExist(origin)
            if cached_template:
                return cached_template

            try:
                template = read_theme_file_from_s3(origin.name)
            except:
                # Cache that we tried this file
                cache.set(cache_key, "tried")
                raise TemplateDoesNotExist(origin)
            cache.set(cache_key, template)

            cache_group_key = "%s.theme_files_cache_list" % settings.SITE_CACHE_KEY
            cache_group_list = cache.get(cache_group_key)
            if cache_group_list is None:
                cache.set(cache_group_key, [cache_key])
            else:
                cache_group_list += [cache_key]
                cache.set(cache_group_key, cache_group_list)

            return template

        else:
            try:
                with open(origin.name) as fp:
                    return fp.read()
            # Python 3 only
            #except FileNotFoundError:
            #    raise TemplateDoesNotExist(origin)
            # Python 2 and 3
            except IOError as e:
                if e.errno == errno.ENOENT:
                    raise TemplateDoesNotExist(origin)
                raise
