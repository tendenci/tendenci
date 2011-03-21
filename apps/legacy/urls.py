from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to


urlpatterns = patterns('legacy.views',
    # static redirects
    url(r'^$', redirect_to, {'url': '/accounts/login/'}),
    url(r'^rss/$', redirect_to, {'url': '/rss'}),

    # module redirects
    url(r'^(art|articles)/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'articles'}),
    url(r'^(rel|releases)/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'news'}),
    url(r'^(cev|calendarevents)/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'events'}),
    url(r'^(cms|contentmanagers)/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'pages'}),
    url(r'^photos/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'photos'}),
    url(r'^photos/albums/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'photo_sets'}),
    url(r'^helpfiles/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'help_files'}),
    url(r'^(q|quotes)/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'quotes'}),
)
