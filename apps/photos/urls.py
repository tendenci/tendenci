from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('',

    ## photos ##

    # /photos/
    url(r'^$', 'photos.views.photos', name="photos"),
    # /photos/details
    url(r'^details/(?P<id>\d+)/$', 'photos.views.details', name="photo_details"),
    # /photos/23
    url(r'^(?P<id>\d+)/$', 'photos.views.photo', name="photo"),
    # /photos/23/in/36
    url(r'^(?P<id>\d+)/in/(?P<set_id>\d+)/$', 'photos.views.photo', name="photo"),
    # /photos/file-upload/
    url(r'^file-upload/$', 'photos.views.file_upload', name="photo_file_upload"),
    # /photos/upload/
    url(r'^upload/$', 'photos.views.upload', name="photo_upload"),
    # /photos/delete/23/
    url(r'^delete/(?P<id>\d+)/$', 'photos.views.destroy', name='photo_destroy'),
    # /photos/edit/23/
    url(r'^edit/(?P<id>\d+)/$', 'photos.views.edit', name='photo_edit'),
    # /photos/edit/23/in/36
    url(r'^edit/(?P<id>\d+)/in/(?P<set_id>\d+)/$', 'photos.views.edit', name='photo_edit'),

    ## swfupload ##

    # /photos/batch-add/
    url(r'^batch-add/$', 'photos.views.photos_batch_add', name='photos_batch_add'),
    # /photos/batch-add/36/
    url(r'^batch-add/(?P<photoset_id>\d+)$', 'photos.views.photos_batch_add', name='photos_batch_add'),
    # /photos/batch-edit/
    url(r'^batch-edit/$', 'photos.views.photos_batch_edit', name='photos.views.photos_batch_edit'),
    # /photos/batch-edit/36
    url(r'^batch-edit/(?P<photoset_id>\d+)$', 'photos.views.photos_batch_edit', name='photos_batch_edit'),

    ## photo-sets ##

    # /photos/set/add/
    url(r'^set/add/$', 'photos.views.photoset_add', name='photoset_add'),
    # /photos/set/edit/23
    url(r'^set/edit/(?P<id>\d+)$', 'photos.views.photoset_edit', name='photoset_edit'),
    # /photos/set/delete/23
    url(r'^set/delete/(?P<id>\d+)$', 'photos.views.photoset_delete', name='photoset_delete'),
    # /photos/set/latest/
    url(r'^set/latest/$', 'photos.views.photoset_view_latest', name='photoset_latest'),
    # /photos/set/23/
    url(r'^set/(?P<id>\d+)/$', 'photos.views.photoset_details', name="photoset_details"),
)