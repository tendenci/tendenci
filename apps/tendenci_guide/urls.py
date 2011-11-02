from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('',
    url(r'^guide/(?P<slug>[\w\-]+)/$', 'tendenci_guide.views.guide_page', name="tendenci_guide.guide_page"),
)

