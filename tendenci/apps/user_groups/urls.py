from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views

urlpath = get_setting('module', 'user_groups', 'url')
if not urlpath:
    urlpath = "groups"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.search, name='groups'),
    re_path(r'^%s/add/$' % urlpath, views.group_add_edit, name='group.add'),
    re_path(r'^%s/search/$' % urlpath, views.search_redirect, name='group.search'),
    re_path(r'^%s/edit_perms/(?P<id>\d+)/$' % urlpath, views.group_edit_perms, name="group.edit_perms"),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.group_delete, name="group.delete"),
    re_path(r'^%s/adduser/redirect/$' % urlpath, views.groupmembership_bulk_add_redirect, name='group.adduser_redirect'),

    re_path(r'^%s/import/add/$' % urlpath, views.import_add, name='group.import_add'),
    re_path(r'^%s/import/preview/(?P<import_id>\d+)/$' % urlpath, views.import_preview, name='group.import_preview'),
    re_path(r'^%s/import/process/(?P<import_id>\d+)/$' % urlpath, views.import_process, name='group.import_process'),
    re_path(r'^%s/import/download_template/$' % urlpath, views.import_download_template, name='group.import_download_template'),

    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/message/$' % urlpath, views.message, name='group.message'),
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/export/(?P<export_target>\w+)/$' % urlpath, views.group_members_export, name='group.members_export'),
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/export/(?P<export_target>\w+)/status/(?P<identifier>[_\d]+)/$' % urlpath, views.group_members_export_status, name='group.members_export_status'),
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/export/(?P<export_target>\w+)/download/(?P<identifier>[_\d]+)/$' % urlpath, views.group_members_export_download, name='group.members_export_download'),
    # The following 3 links are old export urls. They are here to help to render
    # the url template tags for old export in any customized group detail template.
    # Once the links are rendered, they can be resolved by the pattern
    # group.members_export shown above
    # In other words, to remove the following 3 links, we need to update
    # all custom group detail pages.
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/export/members/$' % urlpath, views.group_member_export, name='group.member_export'),
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/export/subscribers/$' % urlpath, views.group_subscriber_export, name='group.subscriber_export'),
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/export/all/$' % urlpath, views.group_all_export, name='group.all_export'),
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/import/subscribers/$' % urlpath, views.group_subscriber_import, name='group.subscriber_import'),
    re_path(r'^%s/(?P<group_slug>[[\w\-\/]+)/edit/$' % urlpath, views.group_add_edit, name='group.edit'),
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/adduser/$' % urlpath, views.groupmembership_bulk_add, name='group.adduser'),
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/edituser/(?P<user_id>\d+)/$' % urlpath, views.groupmembership_add_edit, name='group.edituser'),
    re_path(r'^%s/(?P<slug>[\w\-\/]+)/selfadd/(?P<user_id>\d+)/$' % urlpath, views.group_membership_self_add, name='group.selfadd'),
    re_path(r'^%s/(?P<slug>[\w\-\/]+)/selfremove/(?P<user_id>\d+)/$' % urlpath, views.group_membership_self_remove, name='group.selfremove'),
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/deleteuser/(?P<user_id>\d+)/$' % urlpath, views.groupmembership_delete, name='group.deleteuser'),
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/import/status/(?P<task_id>[-\w]+)/$' % urlpath, views.subscribers_import_status, name='subscribers_import_status'),

    # newsletter subscription_urls
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/newsletters/subscribe/interactive/$' % urlpath, views.subscribe_to_newsletter_interactive, name='group.newsletter_subscribe_interactive'),
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/newsletters/unsubscribe/interactive/$' % urlpath, views.unsubscribe_to_newsletter_interactive, name='group.newsletter_unsubscribe_interactive'),
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/(?P<newsletter_key>[-.\w]+)/newsletters/unsubscribe/noninteractive/$' % urlpath, views.unsubscribe_to_newsletter_noninteractive, name='group.newsletter_unsubscribe_noninteractive'),
    
    re_path(r'^%s/(?P<group_slug>[\w\-\/]+)/$' % urlpath, views.group_detail, name='group.detail'),
]
