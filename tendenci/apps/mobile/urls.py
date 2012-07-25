from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.apps.mobile.views',
    url(r'^toggle_mobile_mode/$', 'toggle_mobile_mode', name="toggle_mobile_mode"),
)
