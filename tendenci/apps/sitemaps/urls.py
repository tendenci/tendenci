from django.conf.urls import patterns
from tendenci.apps.sitemaps import views

urlpatterns = patterns('',
    (r'^$', views.create_sitemap)
)
