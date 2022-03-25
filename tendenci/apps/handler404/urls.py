from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^reports/$', views.reports_404, name="reports-404-count"),
]
