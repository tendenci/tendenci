from django.conf.urls import url
#from . import views
from .feeds import GlobalFeed

urlpatterns = [
    url(r'^$', GlobalFeed(), name="rss.mainrssfeed"),
]
