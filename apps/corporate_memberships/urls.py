from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('corporate_memberships.views',                  
    url(r"^(?P<slug>.*)/add/$", "add", name="corp_memb.add"),
    url(r"^add_conf/(?P<id>\d+)/$", "add_conf", name="corp_memb.add_conf"),
    url(r"^edit/(?P<id>\d+)/$", "edit", name="corp_memb.edit"),
    url(r"^search/$", "search", name="corp_memb.search"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="corp_memb.delete"),
    url(r"^(?P<id>\d+)/$", "view", name="corp_memb.view"),
)