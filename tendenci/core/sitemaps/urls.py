from django.conf.urls.defaults import patterns
from tendenci.core.sitemaps import views

urlpatterns = patterns('',
    (r'^$', views.create_sitemap)
)
