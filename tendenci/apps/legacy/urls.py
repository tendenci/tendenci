from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to

from pluginmanager.models import PluginApp

urlpatterns = patterns('legacy.views',
    # static redirects
    url(r'^$', redirect_to, {'url': '/accounts/login/'}),
    url(r'^users/$', redirect_to, {'url': '/accounts/login/'}),
    url(r'^google/$', redirect_to, {'url': '/search'}),
    url(r'^rss/$', redirect_to, {'url': '/rss'}),

    # module redirects
    url(r'^(art|articles)/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'articles'}),
    url(r'^(rel|releases)/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'news'}),
    url(r'^cev/mon/$', redirect_to, {'url': '/events/'}),
    url(r'^(cev|calendarevents)/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'events'}),
    url(r'^(cms|contentmanagers)/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'pages'}),
    url(r'^(j|jobs)/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'jobs'}),
    url(r'^photos/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'photos'}),
    url(r'^photos/albums/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'photo_sets'}),
    url(r'^helpfiles/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'help_files'}),
)

quotes = PluginApp.objects.filter(is_enabled=True).filter(package__contains='quotes')
if quotes:
    urlpatterns += patterns('legacy.views',
        url(r'^(q|quotes)/?(v/)?((?P<view>(view|search))\.asp|(?P<id>\d+)/?)?$', 'redirect', {'content_type': 'quotes'}),
    )

attorneys = PluginApp.objects.filter(is_enabled=True).filter(package__contains='attorneys')
if attorneys:
    urlpatterns += patterns('legacy.views',
        url(r'^attorneys/?(v/)?((?P<view>(view|search)))\.asp/$', 'redirect', {'content_type': 'attorneys'}),
    )

before_and_after = PluginApp.objects.filter(is_enabled=True).filter(package__contains='before_and_after')
if before_and_after:
    urlpatterns += patterns('legacy.views',
        url(r'^catalogs/?(plasticsurgery/)?((?P<view>(view|search)))\.asp/$', 'redirect', {'content_type': 'before_and_after'}),
    )

products = PluginApp.objects.filter(is_enabled=True).filter(package__contains='products')
if products:
    urlpatterns += patterns('legacy.views',
        url(r'^catalogs/?(items/)?((?P<view>(view|search)))\.asp/$', 'redirect', {'content_type': 'products'}),
    )
