from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views
from django.views.generic import RedirectView

urlpath = get_setting('module', 'users', 'url')
if not urlpath:
    urlpath = "profiles"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.index, name="profile.index"),
    url(r'^%s/admins/$' % urlpath, views.admin_list, name="profile.admins"),
    url(r'^%s/search/$' % urlpath, views.search, name="profile.search"),
    url(r'^%s/add/$' % urlpath, views.add, name="profile.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="profile.edit"),
    url(r'^%s/similar/$' % urlpath, views.similar_profiles, name="profile.similar"),
    url(r'^%s/merge/(?P<sid>\d+)/$' % urlpath, views.merge_profiles, name="profile.merge_view"),
    url(r'^%s/edit_perms/(?P<id>\d+)/$' % urlpath, views.edit_user_perms, name="profile.edit_perms"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="profile.delete"),

    # export profiles
    url(r"^%s/export/$" % urlpath, views.profile_export, name="profile.export"),
    url(r"^%s/export/status/(?P<identifier>\d+)/$" % urlpath,
        views.profile_export_status,
        name="profile.export_status"),
    url(r"^%s/export/download/(?P<identifier>\d+)/$" % urlpath,
        views.profile_export_download,
        name="profile.export_download"),

    # import users
    url(r"^%s/import/$" % urlpath, views.user_import_upload,
        name="profiles.user_import"),
    url(r"^%s/import/download/$" % urlpath, views.download_user_template,
        name="profiles.download_user_template"),
    url(r"^%s/import/preview/(?P<uimport_id>\d+)/$" % urlpath,
        views.user_import_preview,
        name="profiles.user_import_preview"),
    url(r"^%s/import/process/(?P<uimport_id>\d+)/$" % urlpath,
        views.user_import_process,
        name="profiles.user_import_process"),
    url(r"^%s/import/status/(?P<uimport_id>\d+)/$" % urlpath,
        views.user_import_status,
        name="profiles.user_import_status"),
    url(r"^%s/import/get_status/(?P<uimport_id>\d+)/$" % urlpath,
        views.user_import_get_status,
        name="profiles.user_import_get_status"),
    url(r"^%s/import/check_encode_status/(?P<uimport_id>\d+)/$" % urlpath,
        views.user_import_check_preprocess_status,
        name="profiles.user_import_check_preprocess_status"),
    url(r"^%s/import/download_recap/(?P<uimport_id>\d+)/$" % urlpath,
        views.user_import_download_recap,
        name="profiles.user_import_download_recap"),

    # activate inactive user account
    url(r'^%s/activate-email/$' % urlpath, views.activate_email, name="profile.activate_email"),

    url(r'^%s/(?P<username>[+-.\w\d@\s]+)/$' % urlpath, views.index, name='profile'),
    url(r'^%s/(?P<username>[+-.\w\d@\s]+)/groups/edit/$' % urlpath, views.user_groups_edit, name='profile.edit_groups'),
    url(r'^%s/(?P<username>[+-.\w\d@\s]+)/education/edit/$' % urlpath, views.user_education_edit, name='profile.edit_education'),
    url(r'^%s/(?P<username>[+-.\w\d@\s]+)/groups/(?P<membership_id>\d+)/edit/$' % urlpath, views.user_role_edit, name='profile.edit_role'),
    url(r'^%s/(?P<username>[+-.\w\d@\s]+)/memberships/add/$' % urlpath, views.user_membership_add, name='profile.add_membership'),
]

urlpatterns += [
    # Special redirect for user.get_absolute_url
    url(r'^users/(?P<username>[+-.\w\d@\s]+)/$', RedirectView.as_view(url='/%s/%s/' % (urlpath, '%(username)s'), permanent=True)),
]
