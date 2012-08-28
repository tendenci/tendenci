from django.conf.urls.defaults import patterns, url
from django.conf import settings

from tendenci.addons.jobs.views import add, edit, print_view
from tendenci.addons.culintro.forms import CulintroJobForm
from tendenci.addons.culintro.models import CulintroJob

urlpatterns = patterns('tendenci.addons.culintro.views',
    url(r'^culintro-jobs/$', 'search', name="culintro.search"),
    url(r'^culintro-jobs/print-view/(?P<slug>[\w\-\/]+)/$', print_view, name="culintro.print_view"),
    url(r'^culintro-jobs/add/$', add, kwargs={'form_class':CulintroJobForm,
                                         'template_name': settings.PROJECT_ROOT + '/plugins/culintro/templates/culintro/add.html',
                                         'object_type': CulintroJob,
                                         'success_redirect': 'culintro.detail',
                                 }, name="culintro.add"),
    url(r'^culintro-jobs/edit/(?P<id>\d+)/$', edit, kwargs={'form_class':CulintroJobForm,
                                                       'template_name': settings.PROJECT_ROOT + '/plugins/culintro/templates/culintro/edit.html',
                                                       'object_type': CulintroJob,
                                                       'success_redirect': 'culintro.detail',
                                               }, name="culintro.edit"),
    url(r'^culintro-jobs/(?P<slug>[\w\-\/]+)/$', 'detail', name="culintro.detail"),
)
