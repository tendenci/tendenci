# This file is a wrapper around django.templatetags.static which searches for
# static files in relevant themes before defaulting to the static files bundled
# with the apps.

from warnings import warn
import os
from django import template
from django.conf import settings
from django.templatetags.static import (get_static_prefix as _get_static_prefix,
                                        StaticNode)
from django.utils.six.moves.urllib.parse import quote, urljoin
from tendenci.apps.theme.utils import (get_active_theme, get_theme,
                                       get_theme_search_order, is_builtin_theme,
                                       get_builtin_theme_dir, get_theme_root)


register = template.Library()


@register.tag
def get_static_prefix(parser, token):
    template = parser.origin.name
    theme = getattr(parser.origin, 'theme', None)
    theme_str = ('theme "%s"'%(theme) if theme else 'an installed Django app')
    warn('{%% get_static_prefix %%} in template "%s" in %s should be avoided because it does not work with Tendenci themes'%(template, theme_str), DeprecationWarning)
    _get_static_prefix(parser, token)


_cached_theme_search_info = (None, None)
class ThemeStaticNode(StaticNode):

    def url(self, context):
        path = self.path.resolve(context)
        return self.handle_simple(path, self.local_only, self.template, self.theme)

    @classmethod
    def handle_simple(cls, path, local_only, template=None, theme=None):

        active_theme = get_active_theme()
        theme = get_theme(active_theme)
        global _cached_theme_search_info
        cached_theme, theme_search_info = _cached_theme_search_info

        # If the theme changed or the user is previewing a different theme,
        # update _cached_theme_search_info.
        # Note that _cached_theme_search_info may be shared between multiple
        # threads, so you must be careful when reading/writing
        # _cached_theme_search_info to ensure that writes in one thread cannot
        # cause unexpected behavior in another thread that is reading/writing
        # _cached_theme_search_info at the same time.
        if cached_theme != theme:
            theme_search_info = []
            for cur_theme in get_theme_search_order(theme):
                if is_builtin_theme(cur_theme):
                    cur_theme_dir = get_builtin_theme_dir(cur_theme)
                    static_path = os.path.join(settings.STATIC_ROOT, 'themes', cur_theme_dir)
                    if not os.path.isdir(static_path):
                        continue
                    local_static_url = '%sthemes/%s/'%(settings.LOCAL_STATIC_URL, cur_theme_dir)
                    static_url = '%sthemes/%s/'%(settings.STATIC_URL, cur_theme_dir)
                    theme_search_info.append((static_path, local_static_url, static_url))
                else:
                    cur_theme_root = get_theme_root(cur_theme)
                    for static_dir in ['media', 'static']:
                        static_path = os.path.join(cur_theme_root, static_dir)
                        if not os.path.isdir(static_path):
                            continue
                        local_static_url = static_url = '/themes/'+cur_theme+'/'+static_dir+'/'
                        if settings.USE_S3_STORAGE:
                            static_url = '%s/%s/%s/themes/%s/%s/'%(
                                settings.S3_ROOT_URL, settings.AWS_STORAGE_BUCKET_NAME,
                                settings.AWS_LOCATION, cur_theme, static_dir
                            )
                        theme_search_info.append((static_path, local_static_url, static_url))
            if theme == active_theme:
                _cached_theme_search_info = (theme, theme_search_info)

        # Search for static file in themes
        for static_path, local_static_url, static_url in theme_search_info:
            if not os.path.exists(os.path.join(static_path, path)):
                continue
            return urljoin((local_static_url if local_only else static_url), quote(path))

        # Warn about static files that don't exist in either a theme or
        # STATIC_ROOT
        if not os.path.exists(os.path.join(settings.STATIC_ROOT, path)):
            if not template:
                call = ('local_static' if local_only else 'static')
                warn('%s() call references non-existent static path "%s"'%(call, path))
            else:
                tag = ('{% local_static %}' if local_only else '{% static %}')
                theme_str = ('theme "%s"'%(theme) if theme else 'an installed Django app')
                warn('%s in template "%s" in %s references non-existent static path "%s"'%(tag, template, theme_str, path))

        # Handle {% local_static %} for files not found in a theme
        if local_only:
            return urljoin(settings.LOCAL_STATIC_URL, quote(path))

        # Default to standard Django {% static %} behavior
        return super(ThemeStaticNode, cls).handle_simple(path)

@register.tag('static')
def do_static(parser, token, local_only=False):
    node = ThemeStaticNode.handle_token(parser, token)
    node.local_only = local_only
    node.template = parser.origin.name
    node.theme = getattr(parser.origin, 'theme', None)
    return node

@register.tag('local_static')
def do_local_static(parser, token):
    return do_static(parser, token, True)

def static(path, local_only=False):
    return ThemeStaticNode.handle_simple(path, local_only)

def local_static(path):
    static(path, True)
