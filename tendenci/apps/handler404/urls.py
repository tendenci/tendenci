from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^reports/$', views.reports_404, name="reports-404-count"),
]
