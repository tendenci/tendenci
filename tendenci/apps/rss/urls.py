from django.urls import re_path
#from . import views
from .feeds import RSSFeed

app_name = 'rss'

urlpatterns = [
    re_path(r'^$', RSSFeed(), name="rss.mainrssfeed")
]
