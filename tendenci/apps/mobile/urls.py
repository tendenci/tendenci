from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('mobile',
    url(r'^toggle_mobile_mode/$', 'views.toggle_mobile_mode', name="toggle_mobile_mode"),
)
