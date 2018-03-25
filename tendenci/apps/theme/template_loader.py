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

from tendenci.apps.theme.utils import (get_active_theme, get_theme,
                                       get_theme_search_order, is_builtin_theme,
                                       get_theme_root)
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
        self.cached_theme_search_info = (None, None)
        super(Loader, self).__init__(engine)

    def get_template_sources(self, template_name, template_dirs=None):
        """
        Return possible absolute paths to "template_name" in the current theme
        and any themes it inherits from.
        Any paths that don't lie inside one of the template dirs are excluded
        from the result set for security reasons.
        """
        current_request = get_current_request()
        mobile = (current_request and current_request.mobile)

        active_theme = get_active_theme()
        theme = get_theme(active_theme)
        cached_theme, theme_search_info = self.cached_theme_search_info

        # If the theme changed or the user is previewing a different theme,
        # recalculate theme_search_info.
        # Note that this Loader instance may be shared between multiple threads,
        # so you must be careful when reading/writing
        # self.cached_theme_search_info to ensure that writes in one thread
        # cannot cause unexpected behavior in another thread that is
        # reading/writing self.cached_theme_search_info at the same time.
        if cached_theme != theme:
            theme_search_info = []
            for cur_theme in get_theme_search_order(theme):
                if is_builtin_theme(cur_theme) or not settings.USE_S3_THEME:
                    theme_search_info.append((cur_theme, get_theme_root(cur_theme), False))
                else:
                    theme_search_info.append((cur_theme, cur_theme, True))
            if theme == active_theme:
                self.cached_theme_search_info = (theme, theme_search_info)

        for cur_theme, cur_theme_root, use_s3_theme in theme_search_info:
            for template_path in (['mobile', 'templates'] if mobile else ['templates']):
                if not use_s3_theme:
                    try:
                        template_file = safe_join(cur_theme_root, template_path, template_name)
                    except SuspiciousFileOperation:
                        # The joined path was located outside of template_path,
                        # although it might be inside another one, so this isn't
                        # fatal.
                        continue
                else:
                    template_file = os.path.join(cur_theme_root, template_path, template_name)
                origin = Origin(name=template_file, template_name=template_name, loader=self)
                origin.theme = cur_theme
                origin.use_s3_theme = use_s3_theme
                yield origin

    def get_contents(self, origin):
        if not origin.use_s3_theme:
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

        else:
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
