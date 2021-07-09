from django.urls import path, re_path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    re_path(r'^manage_payment_info/(?P<recurring_payment_id>\d+)/$', views.manage_payment_info,
        name="recurring_payment.authnet.manage_payment_info"),
    re_path(r'^update_payment_info/(?P<recurring_payment_id>\d+)/$', views.update_payment_info,
        name="recurring_payment.authnet.update_payment_info"),
    re_path(r'^empty/$', TemplateView.as_view(template_name='recurring_payments/authnet/empty.html')),
    re_path(r'^iframe_communicator/$', TemplateView.as_view(template_name='recurring_payments/authnet/IframeCommunicator.html'),
        name='recurring_payment.authnet.iframe_communicator'),
    re_path(r'^update_payment_profile_local/$', views.update_payment_profile_local,
        name="recurring_payment.authnet.update_payment_profile_local"),
    re_path(r'^retrieve_token/$', views.retrieve_token,
        name="recurring_payment.authnet.retrieve_token"),
]
