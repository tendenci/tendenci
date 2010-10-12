from django.conf.urls.defaults import *

urlpatterns = patterns('plugins.blog.views',
    url(r'^blog/$', 'list', name="blog-list"),
    url(r'^blog/(\d+)/$', 'detail', name="blog-detail"),
)
