from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from django.views.generic import RedirectView

urlpath = get_setting('module', 'users', 'url')
if not urlpath:
    urlpath = "profiles"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.index, name="profile.index"),
    re_path(r'^%s/admins/$' % urlpath, views.admin_list, name="profile.admins"),
    re_path(r'^%s/search/$' % urlpath, views.search, name="profile.search"),
    re_path(r'^%s/add/$' % urlpath, views.add, name="profile.add"),
    re_path(r'^%s/upload-photo/$' % urlpath, views.profile_photo_upload, name="profile.upload_photo"),
    re_path(r'^%s/upload-photo/(?P<id>\d+)/$' % urlpath, views.profile_photo_upload, name="profile.upload_photo"),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="profile.edit"),
    re_path(r'^%s/similar/$' % urlpath, views.similar_profiles, name="profile.similar"),
    re_path(r'^%s/merge/(?P<sid>\d+)/$' % urlpath, views.merge_profiles, name="profile.merge_view"),
    re_path(r'^%s/edit_perms/(?P<id>\d+)/$' % urlpath, views.edit_user_perms, name="profile.edit_perms"),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="profile.delete"),

    # export profiles
    re_path(r"^%s/export/$" % urlpath, views.profile_export, name="profile.export"),
    re_path(r"^%s/export/status/(?P<identifier>\d+)/$" % urlpath,
        views.profile_export_status,
        name="profile.export_status"),
    re_path(r"^%s/export/download/(?P<identifier>\d+)/$" % urlpath,
        views.profile_export_download,
        name="profile.export_download"),

    # import users
    re_path(r"^%s/import/$" % urlpath, views.user_import_upload,
        name="profiles.user_import"),
    re_path(r"^%s/import/download/$" % urlpath, views.download_user_template,
        name="profiles.download_user_template"),
    re_path(r"^%s/import/preview/(?P<uimport_id>\d+)/$" % urlpath,
        views.user_import_preview,
        name="profiles.user_import_preview"),
    re_path(r"^%s/import/process/(?P<uimport_id>\d+)/$" % urlpath,
        views.user_import_process,
        name="profiles.user_import_process"),
    re_path(r"^%s/import/status/(?P<uimport_id>\d+)/$" % urlpath,
        views.user_import_status,
        name="profiles.user_import_status"),
    re_path(r"^%s/import/get_status/(?P<uimport_id>\d+)/$" % urlpath,
        views.user_import_get_status,
        name="profiles.user_import_get_status"),
    re_path(r"^%s/import/check_encode_status/(?P<uimport_id>\d+)/$" % urlpath,
        views.user_import_check_preprocess_status,
        name="profiles.user_import_check_preprocess_status"),
    re_path(r"^%s/import/download_recap/(?P<uimport_id>\d+)/$" % urlpath,
        views.user_import_download_recap,
        name="profiles.user_import_download_recap"),

    # activate inactive user account
    re_path(r'^%s/activate-email/$' % urlpath, views.activate_email, name="profile.activate_email"),

    re_path(r'^%s/(?P<username>[+-.\w\d@\s]+)/$' % urlpath, views.index, name='profile'),
    re_path(r'^%s/(?P<username>[+-.\w\d@\s]+)/groups/edit/$' % urlpath, views.user_groups_edit, name='profile.edit_groups'),
    re_path(r'^%s/(?P<username>[+-.\w\d@\s]+)/education/edit/$' % urlpath, views.user_education_edit, name='profile.edit_education'),
    re_path(r'^%s/(?P<username>[+-.\w\d@\s]+)/groups/(?P<membership_id>\d+)/edit/$' % urlpath, views.user_role_edit, name='profile.edit_role'),
    re_path(r'^%s/(?P<username>[+-.\w\d@\s]+)/memberships/add/$' % urlpath, views.user_membership_add, name='profile.add_membership'),
]

urlpatterns += [
    # Special redirect for user.get_absolute_url
    re_path(r'^users/(?P<username>[+-.\w\d@\s]+)/$', RedirectView.as_view(url='/%s/%s/' % (urlpath, '%(username)s'), permanent=True)),
]
