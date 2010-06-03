from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('usergroups.views',
    url(r'^$',                              'group_search',     name='groups'),
    url(r'^add/$',                          'group_add_edit', name='group_add'),
    url(r'^search/$',                       'group_search',   name='group_search'),
    url(r'^edit_perms/(?P<id>\d+)/$',       'group_edit_perms', name="group.edit_perms"),
    url(r'^(?P<group_slug>[-.\w]+)/$',      'group_detail',   name='group_detail'),
    url(r'^(?P<group_slug>[-.\w]+)/edit/$', 'group_add_edit', name='group_edit'),
    url(r'^(?P<group_slug>[-.\w]+)/adduser/$', 'groupmembership_add_edit', name='group_adduser'),
    url(r'^(?P<group_slug>[-.\w]+)/edituser/(?P<user_id>\d+)/$', 'groupmembership_add_edit', name='group_edituser'),
)
