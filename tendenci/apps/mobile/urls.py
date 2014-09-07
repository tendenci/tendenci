from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.core.mobile.views',
    url(r'^toggle_mobile_mode/$', 'toggle_mobile_mode', name="toggle_mobile_mode"),
)
