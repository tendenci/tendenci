from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.search, name="invoices"),
    url(r'^export/$', views.export, name="invoice.export"),
    url(r"^export/status/(?P<identifier>\d+)/$", views.export_status, name="invoice.export_status"),
    url(r"^export/download/(?P<identifier>\d+)/$", views.export_download, name="invoice.export_download"),
    url(r'^(?P<id>\d+)/(?P<guid>[\d\w-]+)?$', views.view, name="invoice.view"),
    url(r'^print/(?P<id>\d+)/(?P<guid>[\d\w-]+)?$', views.view,
        {'template_name': 'invoices/print_view.html'}, name="invoice.print_view"),
    url(r'^adjust/(?P<id>\d+)/$', views.adjust, name="invoice.adjust"),
    url(r'^detail/(?P<id>\d+)/$', views.detail, name="invoice.detail"),
    url(r'^download/(?P<id>\d+)/$', views.download_pdf, name="invoice.download"),
    url(r'^email/(?P<invoice_id>\d+)/$', views.email_invoice, name="invoice.email"),
    url(r'^mark-as-paid/(?P<id>\d+)/$', views.mark_as_paid, name="invoice.mark_as_paid"),
#     url(r'^unvoid-invoice/(?P<id>\d+)/$', views.unvoid_invoice, name="invoice.unvoid_invoice"),
    url(r'^void-invoice/(?P<id>\d+)/$', views.void_invoice, name="invoice.void_invoice"),
    url(r'^void_payment/(?P<id>\d+)/$', views.void_payment, name="invoice.void_payment"),
    url(r'^search/$', views.search, name="invoice.search"),
    # invoice reports
    url(r'^report/top_spenders/$', views.report_top_spenders, name="reports-top-spenders"),
]
