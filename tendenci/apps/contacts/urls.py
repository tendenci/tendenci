from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^contacts/$', views.search, name="contacts"),
    re_path(r'^contacts/(?P<id>\d+)/$', views.details, name="contact"),
    re_path(r'^contacts/search/$', views.search_redirect, name="contact.search"),
    re_path(r'^contacts/print-view/(?P<id>\d+)/$', views.print_view, name="contact.print_view"),
    re_path(r'^contacts/delete/(?P<id>\d+)/$', views.delete, name="contact.delete"),

    # site contact form
    re_path(r'^contact/$', views.index, name="form"),
    re_path(r'^contact/confirmation$', views.confirmation, name="form.confirmation"),

]
