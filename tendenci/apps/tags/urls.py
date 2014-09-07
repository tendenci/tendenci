from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.apps.tags.views',
    url(r'^$', 'tags_list', name="tags_list"),
    url(r'^(?P<id>\d+)/$', 'detail', name="tag.detail"),
    url(r'^autocomplete/$', 'autocomplete', name="tag.autocomplete"),
)
