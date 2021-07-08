from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.search, name="invoices"),
    re_path(r'^export/$', views.export, name="invoice.export"),
    re_path(r"^export/status/(?P<identifier>\d+)/$", views.export_status, name="invoice.export_status"),
    re_path(r"^export/download/(?P<identifier>\d+)/$", views.export_download, name="invoice.export_download"),
    re_path(r'^(?P<id>\d+)/(?P<guid>[\d\w-]+)?$', views.view, name="invoice.view"),
    re_path(r'^print/(?P<id>\d+)/(?P<guid>[\d\w-]+)?$', views.view,
        {'template_name': 'invoices/print_view.html'}, name="invoice.print_view"),
    re_path(r'^adjust/(?P<id>\d+)/$', views.adjust, name="invoice.adjust"),
    re_path(r'^detail/(?P<id>\d+)/$', views.detail, name="invoice.detail"),
    re_path(r'^download/(?P<id>\d+)/$', views.download_pdf, name="invoice.download"),
    re_path(r'^email/(?P<invoice_id>\d+)/$', views.email_invoice, name="invoice.email"),
    re_path(r'^mark-as-paid/(?P<id>\d+)/$', views.mark_as_paid, name="invoice.mark_as_paid"),
#     re_path(r'^unvoid-invoice/(?P<id>\d+)/$', views.unvoid_invoice, name="invoice.unvoid_invoice"),
    re_path(r'^void-invoice/(?P<id>\d+)/$', views.void_invoice, name="invoice.void_invoice"),
    re_path(r'^void_payment/(?P<id>\d+)/$', views.void_payment, name="invoice.void_payment"),
    re_path(r'^search/$', views.search, name="invoice.search"),
    # invoice reports
    re_path(r'^report/top_spenders/$', views.report_top_spenders, name="reports-top-spenders"),
    re_path(r'^report/overview/$', views.reports_overview, name="invoices.reports_overview"),
]
