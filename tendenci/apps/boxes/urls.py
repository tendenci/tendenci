from django.conf.urls import url


urlpatterns = [
    url(r'^export/$', 'tendenci.apps.boxes.views.export', name='boxes.export'),
]
