from django.urls import path, re_path

from tendenci.apps.site_settings.utils import get_setting
from .views import LoginView, AuthorizeView, Oauth2LogoutView

#urlpath = get_setting('module', 'oauth2_client', 'url') or 'oauth2'

urlpatterns = [
        re_path(r'^login/$',
            LoginView.as_view(), name='oauth2_login'),

        re_path(r'^auth/$',
            AuthorizeView.as_view(), name='oauth2_auth'),
        
        re_path(r'^logout/$',
            Oauth2LogoutView.as_view(template_name='accounts/logout.html'),
             name='oauth2_logout'),
]
