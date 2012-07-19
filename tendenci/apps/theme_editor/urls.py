from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('',
    url(r'^apps/$', 'theme_editor.views.app_list', name="theme_editor.app_list"),
    url(r'^templates/(?P<app>[\w.]+)?/?$', 'theme_editor.views.original_templates', name="theme_editor.original_templates"),
    url(r'^copy_to_theme/(?P<app>[\w.]+)?/?$', 'theme_editor.views.copy_to_theme', name="theme_editor.copy_to_theme"),
    url(r'^editor/$', 'theme_editor.views.edit_file', name="theme_editor.editor"),
    url(r'^get-version/(\d+)/$', 'theme_editor.views.get_version', name="theme_editor.get_version"),
    url(r'^delete/$', 'theme_editor.views.delete_file', name="theme_editor.delete"),
    url(r'^upload/$', 'theme_editor.views.upload_file', name="theme_editor.upload"),
)

