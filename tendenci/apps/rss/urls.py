from django.urls import re_path
#from . import views
from .feeds import GlobalFeed

urlpatterns = [
    re_path(r'^$', GlobalFeed(), name="rss.mainrssfeed"),
]
