from django.conf.urls.defaults import patterns, url
from contacts.feeds import LatestEntriesFeed

urlpatterns = patterns('contacts',                  
    url(r'^$', 'views.index', name="contact"),
    url(r'^(?P<id>\d+)/$', 'views.index', name="contact"),
    url(r'^search/$', 'views.search', name="contact.search"),
    url(r'^print-view/(?P<id>\d+)/$', 'views.print_view', name="contact.print_view"),
    url(r'^add/$', 'views.add', name="contact.add"),
    url(r'^delete/(?P<id>\d+)/$', 'views.delete', name="contact.delete"),
    # comment: add, edit, delete
#    url(r'^(?P<id>\d+)/comment/add/$', 'views.edit', name="contact.comment.add"),
#    url(r'^(?P<id>\d+)/comment/edit/$', 'views.edit', name="contact.comment.edit"),
#    url(r'^(?P<id>\d+)/comment/delete/$', 'views.edit', name="contact.comment.delete"),
    # feed(s)
    url(r'^feed/$', LatestEntriesFeed(), name='contact.feed'),
)