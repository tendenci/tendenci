# Copyright (c) 2008 Joost Cassee
# Licensed under the terms of the MIT License (see LICENSE.txt)
from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^js/textareas/(?P<name>.+)/$', views.textareas_js,
        name='tinymce-js'),
    re_path(r'^js/textareas/(?P<name>.+)/(?P<lang>.*)$', views.textareas_js,
        name='tinymce-js-lang'),
    re_path(r'^spellchecker/$', views.spell_check, name='tinymce-spellcheck'),
    re_path(r'^flatpages_link_list/$', views.flatpages_link_list),
    re_path(r'^compressor/$', views.compressor, name='tinymce-compressor'),
    re_path(r'^filebrowser/$', views.filebrowser, name='tinymce-filebrowser'),
    re_path(r'^preview/(?P<name>.+)/$', views.preview, name='tinymce-preview'),
]
