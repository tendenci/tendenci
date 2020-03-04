from django.conf.urls import url
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
    url(r'^activate/(?P<activation_key>\w+)/$',
        reg_views.activate,
        {'template_name': 'accounts/activate.html'},
        name='registration_activate'),

    url(r'^login/$',
        views.login,
        {'template_name': 'accounts/login.html'},
        name='auth_login'),

    url(r'^logout/$',
        LogoutView.as_view(template_name='accounts/logout.html'),
        name='auth_logout'),

    url(r'^password/change/(?P<id>\d+)/$',
        prof_views.password_change,
        name='auth_password_change'),

    url(r'^password/change/done/(?P<id>\d+)/$',
        prof_views.password_change_done,
        name='auth_password_change_done'),

    url(r'^password/reset/$',
        views.password_reset,
        name='auth_password_reset'),

    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        PasswordResetConfirmView.as_view(form_class=forms.SetPasswordCustomForm,
                                         template_name='registration/custom_password_reset_confirm.html'),
        name='password_reset_confirm'),

    url(r'^password/reset/complete/$',
        PasswordResetCompleteView.as_view(template_name='registration/custom_password_reset_complete.html'),
        name='password_reset_complete'),

    url(r'^password/reset/done/$',
        PasswordResetDoneView.as_view(template_name='registration/custom_password_reset_done.html'),
        name='password_reset_done'),

    url(r'^register/$',
        views.register,
        {'form_class' : forms.RegistrationCustomForm, 'template_name': 'accounts/registration_form.html'},
        name='registration_register'),

    url(r'^register/event/(?P<event_id>\d+)/$',
        views.register,
        {'form_class' : forms.RegistrationCustomForm, 'template_name': 'accounts/registration_form.html'},
        name='registration_event_register'),

    url(r'^register/complete/$',
        TemplateView.as_view(template_name='accounts/registration_complete.html'),
        name='registration_complete'),
]
