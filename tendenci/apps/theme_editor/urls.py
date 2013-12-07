from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('tendenci.apps.theme_editor.views',
    url(r'^apps/$', 'app_list', name="theme_editor.app_list"),
    url(r'^templates/(?P<app>[\w.]+)?/?$', 'original_templates', name="theme_editor.original_templates"),
    url(r'^copy_to_theme/(?P<app>[\w.]+)?/?$', 'copy_to_theme', name="theme_editor.copy_to_theme"),
    url(r'^editor/$', 'edit_file', name="theme_editor.editor"),
    url(r'^get-version/(\d+)/$', 'get_version', name="theme_editor.get_version"),
    url(r'^delete/$', 'delete_file', name="theme_editor.delete"),
    url(r'^upload/$', 'upload_file', name="theme_editor.upload"),
    url(r'^theme_picker/$', 'theme_picker', name='theme_editor.picker'),
    url(r'^theme_color/$', 'theme_color', name='theme_editor.color'),
    url(r'^themes/get/$', 'get_themes', name='theme_editor.get_themes'),
    url(r'^create_template/$', 'create_new_template', name='theme_editor.create_new_template'),
)
