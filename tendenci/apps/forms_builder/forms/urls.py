from django.urls import path, re_path
from tendenci.apps.forms_builder.forms.signals import init_signals
from tendenci.apps.site_settings.utils import get_setting
from . import views

# See also: django.core.validators.slug_re
slug_re = "[-a-zA-Z0-9_]+"

init_signals()

urlpath = get_setting('module', 'forms', 'url')
if not urlpath:
    urlpath = "forms"

urlpatterns = [
    # Form search/list
    re_path(fr"^{urlpath}/$", views.search, name="forms"),

    # Form design
    re_path(fr"^{urlpath}/add/$", views.add, name="form_add"),
    re_path(fr"^{urlpath}/export/$", views.export, name="form_export"),
    re_path(fr"^{urlpath}/update_fields/(?P<id>\d+)$", views.update_fields, name="form_field_update"),
    re_path(fr"^{urlpath}/edit/(?P<id>\d+)$", views.edit, name="form_edit"),
    re_path(fr"^{urlpath}/delete/(?P<id>\d+)$", views.delete, name="form_delete"),
    re_path(fr"^{urlpath}/copy/(?P<id>\d+)$", views.copy, name="form_copy"),
    re_path(fr"^{urlpath}/payment/(?P<invoice_id>\d+)/(?P<invoice_guid>[\d\w-]+)?/$", views.form_entry_payment, name="form_entry_payment"),

    # Form use
    re_path(fr"^{urlpath}/files/(?P<id>\d+)$", views.files, name="form_files"),
    re_path(fr"^{urlpath}/(?P<slug>{slug_re})/sent/$", views.form_sent, name="form_sent"),
    re_path(fr"^{urlpath}/(?P<slug>{slug_re})/$", views.form_detail, name="form_detail"),

    # Form entry management
    re_path(fr"^{urlpath}/entries/(?P<id>\d+)$", views.entries, name="form_entries"),
    re_path(fr"^{urlpath}/entries/delete/(?P<id>\d+)$", views.entry_delete, name="form_entry_delete"),
    re_path(fr"^{urlpath}/entries/export/(?P<id>\d+)/full$", views.entries_export,
            {'include_files': True, }, name="form_entries_export_full"),
    re_path(fr'^{urlpath}/entries/export/(?P<task_id>[-\w]+)/status/$', views.entries_export_status, name="form_entries_export_status"),
    re_path(fr'^{urlpath}/entries/export/(?P<task_id>[-\w]+)/check/$', views.entries_export_check, name="form_entries_export_check"),
    re_path(fr'^{urlpath}/entries/export/(?P<task_id>[-\w]+)/download/$', views.entries_export_download, name="form_entries_export_download"),

    re_path(fr"^{urlpath}/entry/(?P<id>\d+)$", views.entry_detail, name="form_entry_detail"),

    # Form memory management
    re_path(fr"^{urlpath}/memories/(?P<id>\d+)$", views.memories, name="form_memories")
]
