from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('corporate_memberships.views', 
    url(r'^$', 'search', name="corp_memb"),                 
    url(r"^(?P<slug>.*)/add/$", "add", name="corp_memb.add"),
    url(r"^add_conf/(?P<id>\d+)/$", "add_conf", name="corp_memb.add_conf"),
    url(r"^edit/(?P<id>\d+)/$", "edit", name="corp_memb.edit"),
    url(r"^edit_reps/(?P<id>\d+)/$", "edit_reps", name="corp_memb.edit_reps"),
    url(r"^search/$", "search", name="corp_memb.search"),
    url(r"^index/$", "index", name="corp_memb.index"),
    url(r'^roster/$', 'roster_search', name="corp_memb.roster_search"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="corp_memb.delete"),
    url(r'^delete_rep/(?P<id>\d+)/$', 'delete_rep', name="corp_memb.delete_rep"),
    #(r'^renew/(?P<id>\d+)/$', CorpMembRenewFormPreview(CorpMembRenewForm)),
    url(r"^renew/(?P<id>\d+)/$", "renew", name="corp_memb.renew"),
    url(r"^renew_conf/(?P<id>\d+)/$", "renew_conf", name="corp_memb.renew_conf"),
    url(r"^approve/(?P<id>\d+)/$", "approve", name="corp_memb.approve"),
    url(r"^(?P<id>\d+)/$", "view", name="corp_memb.view"),
)