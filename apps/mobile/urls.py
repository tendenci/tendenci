from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('mobile',
    url(r'^toggle_mobile_mode/(?P<redirect_url>\w+)/$', 'views.toggle_mobile_mode', name="toggle_mobile_mode"),
)
