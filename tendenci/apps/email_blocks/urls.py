from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.apps.email_blocks.views',
    url(r'^$', 'search', name="email_blocks"),
    url(r'^(?P<id>\d+)/$', 'view', name="email_block.view"),
    url(r'^search/$', 'search', name="email_block.search"),
    url(r'^add/$', 'add', name="email_block.add"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="email_block.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="email_block.delete"),
)