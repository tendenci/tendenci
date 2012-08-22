from django.conf.urls.defaults import patterns, url
from django.conf import settings

from jobs.views import add, edit, print_view
from culintro.forms import CulintroJobForm
from culintro.models import CulintroJob

urlpatterns = patterns('culintro.views',
    url(r'^culintro/$', 'search', name="culintro.search"),
    url(r'^culintro/print-view/(?P<slug>[\w\-\/]+)/$', print_view, name="culintro.print_view"),
    url(r'^culintro/add/$', add, kwargs={'form_class':CulintroJobForm,
                                         'template_name': settings.PROJECT_ROOT + '/plugins/culintro/templates/culintro/add.html',
                                         'object_type': CulintroJob,
                                         'success_redirect': 'culintro.detail',
                                 }, name="culintro.add"),
    url(r'^culintro/edit/(?P<id>\d+)/$', edit, kwargs={'form_class':CulintroJobForm,
                                                       'template_name': settings.PROJECT_ROOT + '/plugins/culintro/templates/culintro/edit.html',
                                                       'object_type': CulintroJob,
                                                       'success_redirect': 'culintro.detail',
                                               }, name="culintro.edit"),
    url(r'^culintro/(?P<slug>[\w\-\/]+)/$', 'detail', name="culintro.detail"),
)
