from django.urls import path, re_path, include
from tendenci.apps.site_settings.utils import get_setting
from . import views


urlpath = get_setting('module', 'corporate_memberships', 'url')
if not urlpath:
    urlpath = "corporatememberships"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.search, name="corp_memb"),
    re_path(r'^%s/$' % urlpath, views.search, name="corp_memb.search"),
    re_path(r"^%s/profiles/(?P<id>\d+)/$" % urlpath,
        views.corpprofile_view, name="corpmembership.view_profile"),
    re_path(r"^%s/get_app_fields/$" % urlpath,
        views.get_app_fields_json,
        name="corpmemberships.get_app_fields"),
    re_path(r"^%s/add_directory/(?P<id>\d+)/$" % urlpath, views.corp_membership_add_directory, name="corp_membership.add_directory"),

    re_path(r"^%s/applications/(?P<slug>[\w\-]+)/preview/$" % urlpath,
        views.app_preview,  name="corpmembership_app.preview"),

    re_path(r"^%s/applications/add_pre/$" % urlpath,
        views.corpmembership_add_pre, name="corpmembership.add_pre"),

    re_path(r"^%s/applications/add/$" % urlpath,
        views.corpmembership_add, name="corpmembership.add"),

    re_path(r"^%s/(?P<slug>[\w\-]+)/add/$" % urlpath,
        views.corpmembership_add, name="corpmembership.add"),

    re_path(r"^%s/applications/add_conf/(?P<id>\d+)/$" % urlpath,
        views.corpmembership_add_conf, name="corpmembership.add_conf"),

    re_path(r"^%s/applications/edit/(?P<id>\d+)/$" % urlpath,
        views.corpmembership_edit, name="corpmembership.edit"),

    re_path(r"^%s/applications/upgrade/(?P<id>\d+)/$" % urlpath,
        views.corpmembership_upgrade, name="corpmembership.upgrade"),

    re_path(r"^%s/applications/view/(?P<id>\d+)/$" % urlpath,
        views.corpmembership_view, name="corpmembership.view"),

    re_path(r"^%s/applications/search/$" % urlpath,
        views.corpmembership_search, name="corpmembership.search"),

    re_path(r"^%s/applications/cap_status/$" % urlpath,
        views.corpmembership_cap_status, name="corpmembership.cap_status"),

    re_path(r"^%s/applications/pendings/$" % urlpath,
        views.corpmembership_search, {'pending_only': True}, name="corpmembership.pending_list"),

    re_path(r"^%s/applications/mycorps/$" % urlpath,
        views.corpmembership_search, {'my_corps_only': True}, name="corpmembership.mycorps"),

    re_path(r"^%s/applications/index/$" % urlpath,
        views.index, name="corpmembership.index"),

    re_path(r"^%s/applications/delete/(?P<id>\d+)/$" % urlpath,
        views.corpmembership_delete, name="corpmembership.delete"),

    re_path(r"^%s/applications/approve/(?P<id>\d+)/$" % urlpath,
        views.corpmembership_approve, name="corpmembership.approve"),

    re_path(r"^%s/renewal/(?P<id>\d+)/$" % urlpath, views.corp_renew, name="corpmembership.renew"),

    re_path(r"^%s/renewal_conf/(?P<id>\d+)/$" % urlpath, views.corp_renew_conf, name="corpmembership.renew_conf"),

    re_path(r'^%s/roster/$' % urlpath, views.roster_search, name="corpmembership.roster_search"),

    re_path(r"^%s/download/(?P<cm_id>\d+)/(?P<field_id>\d+)/$" % urlpath,
        views.download_file, name="corpmembership.download_file"),


    # import to CorpMembership
    re_path(r"^%s/import/$" % urlpath, views.import_upload, name="corpmembership.import"),
    re_path(r"^%s/import/download/$" % urlpath, views.download_template, name="corpmembership.download_template"),
    re_path(r"^%s/import/preview/(?P<mimport_id>\d+)/$" % urlpath,
        views.import_preview, name="corpmembership.import_preview"),
    re_path(r"^%s/import/check_preprocess_status/(?P<mimport_id>\d+)/$" % urlpath,
        views.check_preprocess_status, name="corpmembership.check_preprocess_status"),
    re_path(r"^%s/import/process/(?P<mimport_id>\d+)/$" % urlpath,
        views.import_process, name="corpmembership.import_process"),
    re_path(r"^%s/import/status/(?P<mimport_id>\d+)/$" % urlpath,
        views.import_status, name="corpmembership.import_status"),
    re_path(r"^%s/import/get_status/(?P<mimport_id>\d+)/$" % urlpath,
        views.import_get_status, name="corpmembership.import_get_status"),

    # export CorpMembership
    re_path(r"^%s/corp-export/$" % urlpath,
        views.corpmembership_export, name="corpmembership.export"),

    # edit corp reps
    re_path(r"^%s/edit_corp_reps/(?P<id>\d+)/$" % urlpath, views.edit_corp_reps, name="corpmembership.edit_corp_reps"),
    re_path(r'^%s/corp_reps_lookup/$' % urlpath, views.corp_reps_lookup, name="corp_membership.reps_lookup"),
    re_path(r'^%s/delete_corp_rep/(?P<id>\d+)/$' % urlpath, views.delete_corp_rep, name="corp_membership.delete_rep"),

    # edit free passes
    re_path(r"^%s/free_passes/edit/(?P<id>\d+)/$" % urlpath,
        views.free_passes_edit, name="corpmembership.free_passes_edit"),

    # notice
    re_path(r'^%s/notices/' % urlpath, include('tendenci.apps.corporate_memberships.notices.urls')),

    # report
    re_path(r"^%s/reports/overview/$" % urlpath, views.overview, name="corp_membership.overview"),


    # reports
    re_path(r'^%s/reports/corp_members_donated/$' % urlpath, views.corp_members_donated, name='reports-corp-members-donated'),
    re_path(r"^%s/reports/active_members_by_type/$" % urlpath, views.report_active_corp_members_by_type, name="reports-active-corp-mems-by-type"),
    re_path(r"^%s/reports/corp_members_by_status/$" % urlpath, views.report_corp_members_by_status, name="reports-corp-mems-by-status"),
    re_path(r"^%s/reports/corp_mems_over_time/$" % urlpath, views.new_over_time_report, name="reports-corp-mems-over-time"),
    re_path(r"^%s/reports/corp_mems_summary/$" % urlpath, views.corp_mems_summary, name="reports-corp-mems-summary"),
    re_path(r"^%s/reports/free_passes_list/$" % urlpath, views.free_passes_list, name="corp_memb.reports.free_passes_list"),
]
