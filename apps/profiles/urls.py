from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('profiles.views',                  
    url(r'^$','index', name="profile.index"),
    url(r'^admins/$', 'admin_list', name="profile.admins"),
    url(r'^search/$', 'search', name="profile.search"),
    url(r'^add/$', 'add', name="profile.add"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="profile.edit"),
    url(r'^edit_perms/(?P<id>\d+)/$', 'edit_user_perms', name="profile.edit_perms"),
    url(r'^avatar/(?P<id>\d+)/$', 'change_avatar', name="profile.change_avatar"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="profile.delete"),
    url(r'^(?P<username>[+-.\w\d@]+)/$','index', name='profile'),
    url(r'^(?P<username>[+-.\w\d@]+)/groups/edit/$','user_groups_edit', name='profile.edit_groups'),
    url(r'^(?P<username>[+-.\w\d@]+)/groups/(?P<membership_id>\d+)/edit/$','user_role_edit', name='profile.edit_role'),
    url(r'^(?P<username>[+-.\w\d@]+)/memberships/add/$','user_membership_add', name='profile.add_membership'),
)
