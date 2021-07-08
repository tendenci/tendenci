from django.urls import path, re_path
from django.contrib.auth.views import (PasswordResetConfirmView, PasswordResetCompleteView, PasswordResetDoneView,
                                       LogoutView)
from . import views, forms
from tendenci.apps.registration import views as reg_views
from tendenci.apps.profiles import views as prof_views
from django.views.generic import TemplateView

urlpatterns = [
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    re_path(r'^activate/(?P<activation_key>\w+)/$',
        reg_views.activate,
        {'template_name': 'accounts/activate.html'},
        name='registration_activate'),

    re_path(r'^login/$',
        views.login,
        {'template_name': 'accounts/login.html'},
        name='auth_login'),

    re_path(r'^logout/$',
        LogoutView.as_view(template_name='accounts/logout.html'),
        name='auth_logout'),

    re_path(r'^password/change/(?P<id>\d+)/$',
        prof_views.password_change,
        name='auth_password_change'),

    re_path(r'^password/change/done/(?P<id>\d+)/$',
        prof_views.password_change_done,
        name='auth_password_change_done'),

    re_path(r'^password/reset/$',
        views.password_reset,
        name='auth_password_reset'),

    re_path(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        PasswordResetConfirmView.as_view(form_class=forms.SetPasswordCustomForm,
                                         template_name='registration/custom_password_reset_confirm.html'),
        name='password_reset_confirm'),

    re_path(r'^password/reset/complete/$',
        PasswordResetCompleteView.as_view(template_name='registration/custom_password_reset_complete.html'),
        name='password_reset_complete'),

    re_path(r'^password/reset/done/$',
        PasswordResetDoneView.as_view(template_name='registration/custom_password_reset_done.html'),
        name='password_reset_done'),

    re_path(r'^register/$',
        views.register,
        {'form_class' : forms.RegistrationCustomForm, 'template_name': 'accounts/registration_form.html'},
        name='registration_register'),

    re_path(r'^register/event/(?P<event_id>\d+)/$',
        views.register,
        {'form_class' : forms.RegistrationCustomForm, 'template_name': 'accounts/registration_form.html'},
        name='registration_event_register'),

    re_path(r'^register/complete/$',
        TemplateView.as_view(template_name='accounts/registration_complete.html'),
        name='registration_complete'),
]
