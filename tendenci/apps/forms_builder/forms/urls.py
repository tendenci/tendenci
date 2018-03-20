from django.conf.urls import url
from tendenci.apps.forms_builder.forms.signals import init_signals
from tendenci.apps.site_settings.utils import get_setting
from . import views

init_signals()

urlpath = get_setting('module', 'forms', 'url')
if not urlpath:
    urlpath = "forms"

urlpatterns = [
    url(r"^%s/$" % urlpath, views.search, name="forms"),
    url(r"^%s/entries/export/(?P<id>\d+)/full$" % urlpath, views.entries_export,
            {'include_files': True,}, name="form_entries_export_full"),
    url(r'^%s/entries/export/(?P<task_id>[-\w]+)/status/$' % urlpath, views.entries_export_status, name="form_entries_export_status"),
    url(r'^%s/entries/export/(?P<task_id>[-\w]+)/check/$' % urlpath, views.entries_export_check, name="form_entries_export_check"),
    url(r'^%s/entries/export/(?P<task_id>[-\w]+)/download/$' % urlpath, views.entries_export_download, name="form_entries_export_download"),

    url(r"^%s/entries/delete/(?P<id>\d+)$" % urlpath, views.entry_delete, name="form_entry_delete"),
    url(r"^%s/add/$" % urlpath, views.add, name="form_add"),
    url(r"^%s/export/$" % urlpath, views.export, name="form_export"),
    url(r"^%s/update_fields/(?P<id>\d+)$" % urlpath, views.update_fields, name="form_field_update"),
    url(r"^%s/edit/(?P<id>\d+)$" % urlpath, views.edit, name="form_edit"),
    url(r"^%s/delete/(?P<id>\d+)$" % urlpath, views.delete, name="form_delete"),
    url(r"^%s/copy/(?P<id>\d+)$" % urlpath, views.copy, name="form_copy"),
    url(r"^%s/entry/(?P<id>\d+)$" % urlpath, views.entry_detail, name="form_entry_detail"),
    url(r"^%s/entries/(?P<id>\d+)$" % urlpath, views.entries, name="form_entries"),
    url(r"^%s/payment/(?P<invoice_id>\d+)/(?P<invoice_guid>[\d\w-]+)?/$" % urlpath, views.form_entry_payment, name="form_entry_payment"),

    url(r"^%s/files/(?P<id>\d+)$" % urlpath, views.files, name="form_files"),
    url(r"^%s/(?P<slug>.*)/sent/$" % urlpath, views.form_sent, name="form_sent"),
    url(r"^%s/(?P<slug>.*)/$" % urlpath, views.form_detail, name="form_detail"),
]
