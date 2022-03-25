from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^editor/$', views.edit_file, name="theme_editor.editor"),
    re_path(r'^theme/copy/$', views.theme_copy, name="theme_editor.theme_copy"),
    re_path(r'^theme/rename/$', views.theme_rename, name="theme_editor.theme_rename"),
    re_path(r'^theme/delete/$', views.theme_delete, name="theme_editor.theme_delete"),
    re_path(r'^apps/$', views.app_list, name="theme_editor.app_list"),
    re_path(r'^templates/$', views.original_templates, name="theme_editor.original_templates"),
    re_path(r'^copy_to_theme/$', views.copy_to_theme, name="theme_editor.copy_to_theme"),
    re_path(r'^get-version/(\d+)/$', views.get_version, name="theme_editor.get_version"),
    re_path(r'^delete/$', views.delete_file, name="theme_editor.delete"),
    re_path(r'^upload/$', views.upload_file, name="theme_editor.upload"),
    re_path(r'^theme_picker/$', views.theme_picker, name='theme_editor.picker'),
    re_path(r'^theme_color/$', views.theme_color, name='theme_editor.color'),
    re_path(r'^themes/get/$', views.get_themes, name='theme_editor.get_themes'),
    re_path(r'^create_template/$', views.create_new_template, name='theme_editor.create_new_template'),
]
