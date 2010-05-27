from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',                  
    url(r'^$', 'profiles.views.search', name="profiles"),
    #url(r'^(?P<id>\d+)/$', 'profiles.views.index', name="profile"),
    url(r'^search/$', 'profiles.views.search', name="profile.search"),
    url(r'^add/$', 'profiles.views.add', name="profile.add"),
    url(r'^edit/(?P<id>\d+)/$', 'profiles.views.edit', name="profile.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'profiles.views.delete', name="profile.delete"),
    url(r'^(?P<username>[-.\w]+)/$', 'profiles.views.index', name='profile'),
)
