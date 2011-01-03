from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('corporate_memberships.views',                  
    url(r"(?P<slug>.*)/add/$", "add", name="corp_memb.add"),
    url(r"add_conf/(?P<id>.*)/$", "add_conf", name="corp_memb.add_conf"),
)