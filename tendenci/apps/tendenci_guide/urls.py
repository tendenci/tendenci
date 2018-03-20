from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^guide/(?P<slug>[\w\-]+)/$', views.guide_page, name="tendenci_guide.guide_page"),
]
