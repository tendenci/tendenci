from django.conf.urls.defaults import *


urlpatterns = patterns("tendenci.apps.forms_builder.forms.views",
    url(r"^$", "search", name="forms"),
    url(r"^entries/export/(?P<id>\d+)/full$", "entries_export", 
            {'include_files': True,}, name="form_entries_export_full"),
    url(r'^entries/export/(?P<task_id>[-\w]+)/status/$', 'entries_export_status', name="form_entries_export_status"),
    url(r'^entries/export/(?P<task_id>[-\w]+)/check/$', 'entries_export_check', name="form_entries_export_check"),
    url(r'^entries/export/(?P<task_id>[-\w]+)/download/$', 'entries_export_download', name="form_entries_export_download"),

    url(r"^entries/delete/(?P<id>\d+)$", "entry_delete", name="form_entry_delete"),
    url(r"^add/$", "add", name="form_add"),
    url(r"^export/$", "export", name="form_export"),
    url(r"^update_fields/(?P<id>\d+)$", "update_fields", name="form_field_update"),
    url(r"^edit/(?P<id>\d+)$", "edit", name="form_edit"),
    url(r"^delete/(?P<id>\d+)$", "delete", name="form_delete"),
    url(r"^copy/(?P<id>\d+)$", "copy", name="form_copy"),
    url(r"^entry/(?P<id>\d+)$", "entry_detail", name="form_entry_detail"),
    url(r"^entries/(?P<id>\d+)$", "entries", name="form_entries"),
    url(r"^payment/(?P<invoice_id>\d+)/(?P<invoice_guid>[\d\w-]+)?/$", "form_entry_payment", name="form_entry_payment"),

    url(r"^files/(?P<id>\d+)$", "files", name="form_files"),
    url(r"^(?P<slug>.*)/sent/$", "form_sent", name="form_sent"),
    url(r"^(?P<slug>.*)/$", "form_detail", name="form_detail"),
)


