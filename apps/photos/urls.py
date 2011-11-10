from django.conf.urls.defaults import url, patterns
from photos.feeds import LatestAlbums, LatestAlbumPhotos



urlpatterns = patterns('',

    ## photos ##

    # /photos/23
    url(r'^(?P<id>\d+)/$', 'photos.views.photo', name="photo"),
    # /photos/23/in/36
    url(r'^(?P<id>\d+)/in/(?P<set_id>\d+)/$', 'photos.views.photo', name="photo"),
    # /photos/23/original
    url(r'^(?P<id>\d+)/original/$', 'photos.views.photo_original', name="photo_original"),
    # /photos/partial/23/in/36
    url(r'^partial/(?P<id>\d+)/in/(?P<set_id>\d+)/$', 'photos.views.photo', kwargs={'partial':True}, name="photo_partial"),
    # /photos/delete/23/
    url(r'^delete/(?P<id>\d+)/$', 'photos.views.delete', name='photo_destroy'),
    # /photos/delete/23/in/36
    url(r'^delete/(?P<id>\d+)/in/(?P<set_id>\d+)/$', 'photos.views.delete', name='photo_destroy'),
    # /photos/edit/23/
    url(r'^edit/(?P<id>\d+)/$', 'photos.views.edit', name='photo_edit'),
    # /photos/edit/23/in/36
    url(r'^edit/(?P<id>\d+)/in/(?P<set_id>\d+)/$', 'photos.views.edit', name='photo_edit'),
    # /photos/sizes/23

    ## sizes ##

    url(r'^sizes/(?P<id>\d+)/$', 'photos.views.sizes', name='photo_sizes'),  # default sizes page
    url(r'^sizes/square/(?P<id>\d+)/$', 'photos.views.sizes', kwargs={'size_name':'square'}, name='photo_square'),
    url(r'^sizes/thumbnail/(?P<id>\d+)/$', 'photos.views.sizes', kwargs={'size_name':'thumbnail'}, name='photo_thumbnail'),
    url(r'^sizes/small/(?P<id>\d+)/$', 'photos.views.sizes', kwargs={'size_name':'small'}, name='photo_small'),
    url(r'^sizes/medium-500/(?P<id>\d+)/$', 'photos.views.sizes', kwargs={'size_name':'medium_500'}, name='photo_medium_500'),
    url(r'^sizes/medium-640/(?P<id>\d+)/$', 'photos.views.sizes', kwargs={'size_name':'medium_640'}, name='photo_medium_640'),
    url(r'^sizes/large/(?P<id>\d+)/$', 'photos.views.sizes', kwargs={'size_name':'large'}, name='photo_large'),
    #url(r'^sizes/original/(?P<id>\d+)/$', 'photos.views.sizes', kwargs={'size_name':'original'}, name='photo_original'),

    ## swfupload ##
    
    # /photos/
    url(r'^$', 'photos.views.photoset_view_latest', name='photoset_latest'),
    url(r'^search/$', 'photos.views.search', name='photos_search'),
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
    url(r'^sets/$', 'photos.views.photoset_view_latest', name='photoset_latest'),
    url(r'^set/latest/$', 'photos.views.photoset_view_latest', name='photoset_latest'),
    # /photos/set/23/
    url(r'^set/(?P<id>\d+)/$', 'photos.views.photoset_details', name="photoset_details"),

    url(r'^feeds/latest-albums/$', LatestAlbums(), name='photo.feed.latest-albums'),

    ## download photo size ##

    url(r'^download/(?P<id>\d+)/(?P<size>\d+x\d+)/$', 'photos.views.photo_size', kwargs={'download':True}, name="photo_download"),
    url(r'^download/crop/(?P<id>\d+)/(?P<size>\d+x\d+)/$', 'photos.views.photo_size', kwargs={'download':True,'crop':True}, name="photo_crop_download"),

    ## dynamic photo size ##

    url(r'^(?P<id>\d+)/(?P<size>\d+x\d+)/$', 'photos.views.photo_size', name="photo.size"),
    url(r'^(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>[crop]*)/$', 'photos.views.photo_size', name="photo.size"),
    url(r'^(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>[crop]*)/(?P<quality>\d+)/$', 'photos.views.photo_size', name="photo.size"),
)
