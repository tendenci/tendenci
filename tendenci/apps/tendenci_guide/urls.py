from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^guide/(?P<slug>[\w\-]+)/$', views.guide_page, name="tendenci_guide.guide_page"),
]
