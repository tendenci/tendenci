from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('',
    url(r'^$', 'theme_editor.views.edit_file', name="theme_editor"),
    url(r'^get-version/(\d+)/$', 'theme_editor.views.get_version', name="theme_editor_get_version"),
    url(r'^original_templates/$', 'theme_editor.views.original_templates', name="original_templates"),
    url(r'^copy_to_theme/$', 'theme_editor.views.copy_to_theme', name="copy_to_theme"),
)

