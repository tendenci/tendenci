from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('corporate_memberships.views',                  
    url(r"(?P<slug>.*)/preview/$", "preview", name="corp_memb.preview"),
)