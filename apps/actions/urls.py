from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('actions.views',                  
    #url(r'^$', 'emails.views.search', name="emails"),
    #url(r'^search/$', 'emails.views.search', name="email.search"),
    url(r'^step4/(?P<action_id>\d+)/$', 'step4', name="action.step4"),
    url(r'^step5/(?P<action_id>\d+)/$', 'step5', name="action.step5"),
    url(r'^confirm/(?P<action_id>\d+)/$', 'confirm', name="action.confirm"),
    url(r'^send/(?P<action_id>\d+)/$', 'send', name="action.send"),
    url(r'^view/(?P<action_id>\d+)/$', 'view', name="action.view"),
)