from django.conf.urls.defaults import patterns, url
from tendenci.apps.user_groups.signals import init_signals
init_signals()

urlpatterns = patterns('tendenci.apps.user_groups.views',
    url(r'^$',                              'search',     name='groups'),
    url(r'^add/$',                          'group_add_edit', name='group.add'),
    url(r'^search/$',                       'search_redirect',   name='group.search'),
    url(r'^edit_perms/(?P<id>\d+)/$',       'group_edit_perms', name="group.edit_perms"),
    url(r'^delete/(?P<id>\d+)/$',       'group_delete', name="group.delete"),
    url(r'^adduser/redirect/$', 'groupmembership_bulk_add_redirect', name='group.adduser_redirect'),

    url(r'^import/add/$', 'import_add', name='group.import_add'),
    url(r'^import/preview/(?P<import_id>\d+)/$', 'import_preview', name='group.import_preview'),
    url(r'^import/process/(?P<import_id>\d+)/$', 'import_process', name='group.import_process'),
    url(r'^import/download_template/$', 'import_download_template', name='group.import_download_template'),

    url(r'^(?P<group_slug>[-.\w]+)/$',      'group_detail',   name='group.detail'),
    url(r'^(?P<group_slug>[-.\w]+)/export/members/$', 'group_member_export', name='group.member_export'),
    url(r'^(?P<group_slug>[-.\w]+)/export/subscribers/$', 'group_subscriber_export', name='group.subscriber_export'),
    url(r'^(?P<group_slug>[-.\w]+)/export/all/$', 'group_all_export', name='group.all_export'),
    url(r'^(?P<group_slug>[-.\w]+)/import/subscribers/$', 'group_subscriber_import', name='group.subscriber_import'),
    url(r'^(?P<group_slug>[-.\w]+)/edit/$', 'group_add_edit', name='group.edit'),
    url(r'^(?P<group_slug>[-.\w]+)/adduser/$', 'groupmembership_bulk_add', name='group.adduser'),
    url(r'^(?P<group_slug>[-.\w]+)/edituser/(?P<user_id>\d+)/$', 'groupmembership_add_edit', name='group.edituser'),
    url(r'^(?P<slug>[-.\w]+)/selfadd/(?P<user_id>\d+)/$', 'group_membership_self_add', name='group.selfadd'),
    url(r'^(?P<slug>[-.\w]+)/selfremove/(?P<user_id>\d+)/$', 'group_membership_self_remove', name='group.selfremove'),
    url(r'^(?P<group_slug>[-.\w]+)/deleteuser/(?P<user_id>\d+)/$', 'groupmembership_delete', name='group.deleteuser'),
    url(r'^(?P<group_slug>[-.\w]+)/import/status/(?P<task_id>[-\w]+)/$', "subscribers_import_status", name='subscribers_import_status'),
)
