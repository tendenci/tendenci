from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('corporate_memberships.views',                  
    url(r"^(?P<slug>.*)/add/$", "add", name="corp_memb.add"),
    url(r"^add_conf/(?P<id>\d+)/$", "add_conf", name="corp_memb.add_conf"),
    url(r"^edit/(?P<id>\d+)/$", "edit", name="corp_memb.edit"),
    url(r"^edit_reps/(?P<id>\d+)/$", "edit_reps", name="corp_memb.edit_reps"),
    url(r"^search/$", "search", name="corp_memb.search"),
    url(r"^index/$", "index", name="corp_memb.index"),
    url(r'^roster/$', 'roster_search', name="corp_memb.roster_search"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="corp_memb.delete"),
    url(r'^delete_rep/(?P<id>\d+)/$', 'delete_rep', name="corp_memb.delete_rep"),
    url(r"^(?P<id>\d+)/$", "view", name="corp_memb.view"),
)