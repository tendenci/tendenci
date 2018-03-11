from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^apps/$', views.app_list, name="theme_editor.app_list"),
    url(r'^templates/(?P<app>[\w.]+)?/?$', views.original_templates, name="theme_editor.original_templates"),
    url(r'^copy_to_theme/(?P<app>[\w.]+)?/?$', views.copy_to_theme, name="theme_editor.copy_to_theme"),
    url(r'^editor/$', views.edit_file, name="theme_editor.editor"),
    url(r'^get-version/(\d+)/$', views.get_version, name="theme_editor.get_version"),
    url(r'^delete/$', views.delete_file, name="theme_editor.delete"),
    url(r'^upload/$', views.upload_file, name="theme_editor.upload"),
    url(r'^theme_picker/$', views.theme_picker, name='theme_editor.picker'),
    url(r'^theme_color/$', views.theme_color, name='theme_editor.color'),
    url(r'^themes/get/$', views.get_themes, name='theme_editor.get_themes'),
    url(r'^create_template/$', views.create_new_template, name='theme_editor.create_new_template'),
]
