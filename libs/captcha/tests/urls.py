from django.conf.urls.defaults import *
urlpatterns = patterns('',
    url(r'test/$','captcha.tests.views.test',name='captcha-test'),
    url(r'test2/$','captcha.tests.views.test_custom_error_message',name='captcha-test-custom-error-message'),
    url(r'',include('captcha.urls')),
)
