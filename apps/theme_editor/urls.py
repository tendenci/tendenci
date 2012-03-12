from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('',
    url(r'^$', 'theme_editor.views.original_templates', name="theme_editor.original_templates"),
    url(r'^editor/$', 'theme_editor.views.edit_file', name="theme_editor.editor"),
    url(r'^get-version/(\d+)/$', 'theme_editor.views.get_version', name="theme_editor.get_version"),
    url(r'^copy_to_theme/$', 'theme_editor.views.copy_to_theme', name="theme_editor.copy_to_theme"),
    url(r'^delete/$', 'theme_editor.views.delete_file', name="theme_editor.delete"),
    url(r'^upload/$', 'theme_editor.views.upload_file', name="theme_editor.upload"),
)

