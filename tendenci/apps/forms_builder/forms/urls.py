from django.urls import path, re_path
from tendenci.apps.forms_builder.forms.signals import init_signals
from tendenci.apps.site_settings.utils import get_setting
from . import views

init_signals()

urlpath = get_setting('module', 'forms', 'url')
if not urlpath:
    urlpath = "forms"

urlpatterns = [
    re_path(r"^%s/$" % urlpath, views.search, name="forms"),
    re_path(r"^%s/entries/export/(?P<id>\d+)/full$" % urlpath, views.entries_export,
            {'include_files': True,}, name="form_entries_export_full"),
    re_path(r'^%s/entries/export/(?P<task_id>[-\w]+)/status/$' % urlpath, views.entries_export_status, name="form_entries_export_status"),
    re_path(r'^%s/entries/export/(?P<task_id>[-\w]+)/check/$' % urlpath, views.entries_export_check, name="form_entries_export_check"),
    re_path(r'^%s/entries/export/(?P<task_id>[-\w]+)/download/$' % urlpath, views.entries_export_download, name="form_entries_export_download"),

    re_path(r"^%s/entries/delete/(?P<id>\d+)$" % urlpath, views.entry_delete, name="form_entry_delete"),
    re_path(r"^%s/add/$" % urlpath, views.add, name="form_add"),
    re_path(r"^%s/export/$" % urlpath, views.export, name="form_export"),
    re_path(r"^%s/update_fields/(?P<id>\d+)$" % urlpath, views.update_fields, name="form_field_update"),
    re_path(r"^%s/edit/(?P<id>\d+)$" % urlpath, views.edit, name="form_edit"),
    re_path(r"^%s/delete/(?P<id>\d+)$" % urlpath, views.delete, name="form_delete"),
    re_path(r"^%s/copy/(?P<id>\d+)$" % urlpath, views.copy, name="form_copy"),
    re_path(r"^%s/entry/(?P<id>\d+)$" % urlpath, views.entry_detail, name="form_entry_detail"),
    re_path(r"^%s/entries/(?P<id>\d+)$" % urlpath, views.entries, name="form_entries"),
    re_path(r"^%s/payment/(?P<invoice_id>\d+)/(?P<invoice_guid>[\d\w-]+)?/$" % urlpath, views.form_entry_payment, name="form_entry_payment"),

    re_path(r"^%s/files/(?P<id>\d+)$" % urlpath, views.files, name="form_files"),
    re_path(r"^%s/(?P<slug>.*)/sent/$" % urlpath, views.form_sent, name="form_sent"),
    re_path(r"^%s/(?P<slug>.*)/$" % urlpath, views.form_detail, name="form_detail"),
]
