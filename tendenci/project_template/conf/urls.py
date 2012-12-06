from django.conf import settings
from django.conf.urls.defaults import *

from tendenci.urls import urlpatterns as tendenci_urls

handler500 = 'tendenci.core.base.views.custom_error'

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = staticfiles_urlpatterns()

if not settings.USE_S3_STORAGE:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
        url(r'^themes/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.THEMES_DIR,
        }),
    )

# Local url patterns for development
try:
    from local_urls import extrapatterns
    urlpatterns += extrapatterns
except ImportError:
    pass

urlpatterns += tendenci_urls
