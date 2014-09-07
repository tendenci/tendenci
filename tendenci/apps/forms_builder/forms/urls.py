from django.conf.urls import patterns, url
from tendenci.apps.site_settings.utils import get_setting

urlpath = get_setting('module', 'forms', 'url')
if not urlpath:
    urlpath = "forms"

urlpatterns = patterns("tendenci.apps.forms_builder.forms.views",
    url(r"^%s/$" % urlpath, "search", name="forms"),
    url(r"^%s/entries/export/(?P<id>\d+)/full$" % urlpath, "entries_export",
            {'include_files': True,}, name="form_entries_export_full"),
    url(r'^%s/entries/export/(?P<task_id>[-\w]+)/status/$' % urlpath, 'entries_export_status', name="form_entries_export_status"),
    url(r'^%s/entries/export/(?P<task_id>[-\w]+)/check/$' % urlpath, 'entries_export_check', name="form_entries_export_check"),
    url(r'^%s/entries/export/(?P<task_id>[-\w]+)/download/$' % urlpath, 'entries_export_download', name="form_entries_export_download"),

    url(r"^%s/entries/delete/(?P<id>\d+)$" % urlpath, "entry_delete", name="form_entry_delete"),
    url(r"^%s/add/$" % urlpath, "add", name="form_add"),
    url(r"^%s/export/$" % urlpath, "export", name="form_export"),
    url(r"^%s/update_fields/(?P<id>\d+)$" % urlpath, "update_fields", name="form_field_update"),
    url(r"^%s/edit/(?P<id>\d+)$" % urlpath, "edit", name="form_edit"),
    url(r"^%s/delete/(?P<id>\d+)$" % urlpath, "delete", name="form_delete"),
    url(r"^%s/copy/(?P<id>\d+)$" % urlpath, "copy", name="form_copy"),
    url(r"^%s/entry/(?P<id>\d+)$" % urlpath, "entry_detail", name="form_entry_detail"),
    url(r"^%s/entries/(?P<id>\d+)$" % urlpath, "entries", name="form_entries"),
    url(r"^%s/payment/(?P<invoice_id>\d+)/(?P<invoice_guid>[\d\w-]+)?/$" % urlpath, "form_entry_payment", name="form_entry_payment"),

    url(r"^%s/files/(?P<id>\d+)$" % urlpath, "files", name="form_files"),
    url(r"^%s/(?P<slug>.*)/sent/$" % urlpath, "form_sent", name="form_sent"),
    url(r"^%s/(?P<slug>.*)/$" % urlpath, "form_detail", name="form_detail"),
)


