from django.conf.urls import url, patterns
from tendenci.apps.photos.feeds import LatestAlbums
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.photos.signals import init_signals

init_signals()

urlpath = get_setting('module', 'photos', 'url')
if not urlpath:
    urlpath = "photos"

urlpatterns = patterns('tendenci.apps',

    ## photos ##

    # /photos/23
    url(r'^%s/(?P<id>\d+)/$' % urlpath, 'photos.views.photo', name="photo"),
    # /photos/23/in/36
    url(r'^%s/(?P<id>\d+)/in/(?P<set_id>\d+)/$' % urlpath, 'photos.views.photo', name="photo"),
    # /photos/23/original
    url(r'^%s/(?P<id>\d+)/original/$' % urlpath, 'photos.views.photo_original', name="photo_original"),
    # /photos/partial/23/in/36
    url(r'^%s/partial/(?P<id>\d+)/in/(?P<set_id>\d+)/$' % urlpath, 'photos.views.photo', kwargs={'partial':True}, name="photo_partial"),
    # /photos/delete/23/
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'photos.views.delete', name='photo_destroy'),
    # /photos/delete/23/in/36
    url(r'^%s/delete/(?P<id>\d+)/in/(?P<set_id>\d+)/$' % urlpath, 'photos.views.delete', name='photo_destroy'),
    # /photos/edit/23/
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'photos.views.edit', name='photo_edit'),
    # /photos/edit/23/in/36
    url(r'^%s/edit/(?P<id>\d+)/in/(?P<set_id>\d+)/$' % urlpath, 'photos.views.edit', name='photo_edit'),
    # /photos/sizes/23

    ## sizes ##

    url(r'^%s/sizes/(?P<id>\d+)/$' % urlpath, 'photos.views.sizes', name='photo_sizes'),  # default sizes page
    url(r'^%s/sizes/square/(?P<id>\d+)/$' % urlpath, 'photos.views.sizes', kwargs={'size_name':'square'}, name='photo_square'),
    url(r'^%s/sizes/thumbnail/(?P<id>\d+)/$' % urlpath, 'photos.views.sizes', kwargs={'size_name':'thumbnail'}, name='photo_thumbnail'),
    url(r'^%s/sizes/small/(?P<id>\d+)/$' % urlpath, 'photos.views.sizes', kwargs={'size_name':'small'}, name='photo_small'),
    url(r'^%s/sizes/medium-500/(?P<id>\d+)/$' % urlpath, 'photos.views.sizes', kwargs={'size_name':'medium_500'}, name='photo_medium_500'),
    url(r'^%s/sizes/medium-640/(?P<id>\d+)/$' % urlpath, 'photos.views.sizes', kwargs={'size_name':'medium_640'}, name='photo_medium_640'),
    url(r'^%s/sizes/large/(?P<id>\d+)/$' % urlpath, 'photos.views.sizes', kwargs={'size_name':'large'}, name='photo_large'),
    #url(r'^sizes/original/(?P<id>\d+)/$', 'photos.views.sizes', kwargs={'size_name':'original'}, name='photo_original'),

    ## swfupload ##

    # /photos/
    url(r'^%s/$' % urlpath, 'photos.views.photoset_view_latest', name='photoset_latest'),
    url(r'^%s/search/$' % urlpath, 'photos.views.search', name='photos_search'),
    # /photos/batch-add/
    url(r'^%s/batch-add/$' % urlpath, 'photos.views.photos_batch_add', name='photos_batch_add'),
    # /photos/batch-add/36/
    url(r'^%s/batch-add/(?P<photoset_id>\d+)$' % urlpath, 'photos.views.photos_batch_add', name='photos_batch_add'),
    # /photos/batch-edit/
    url(r'^%s/batch-edit/$' % urlpath, 'photos.views.photos_batch_edit', name='photos.views.photos_batch_edit'),
    # /photos/batch-edit/36
    url(r'^%s/batch-edit/(?P<photoset_id>\d+)$' % urlpath, 'photos.views.photos_batch_edit', name='photos_batch_edit'),

    ## photo-sets ##

    # /photos/set/add/
    url(r'^%s/set/add/$' % urlpath, 'photos.views.photoset_add', name='photoset_add'),
    # /photos/set/edit/23
    url(r'^%s/set/edit/(?P<id>\d+)$' % urlpath, 'photos.views.photoset_edit', name='photoset_edit'),
    # /photos/set/delete/23
    url(r'^%s/set/delete/(?P<id>\d+)$' % urlpath, 'photos.views.photoset_delete', name='photoset_delete'),
    # /photos/set/latest/
    url(r'^%s/sets/$' % urlpath, 'photos.views.photoset_view_latest', name='photoset_latest'),
    url(r'^%s/set/latest/$' % urlpath, 'photos.views.photoset_view_latest', name='photoset_latest'),
    # /photos/set/23/
    url(r'^%s/set/(?P<id>\d+)/$' % urlpath, 'photos.views.photoset_details', name="photoset_details"),
    # /photos/set/23/zip/
    url(r'^%s/set/(?P<id>\d+)/zip/$' % urlpath, 'photos.views.photoset_zip', name="photoset_zip"),
    url(r'^%s/set/(?P<id>\d+)/zip/status/(?P<task_id>[-\w]+)/$' % urlpath, 'photos.views.photoset_zip_status', name="photoset_zip_status"),

    url(r'^%s/feeds/latest-albums/$' % urlpath, LatestAlbums(), name='photo.feed.latest-albums'),

    ## download photo size ##

    url(r'^%s/download/(?P<id>\d+)/(?P<size>\d+x\d+)/$' % urlpath, 'photos.views.photo_size', kwargs={'download':True}, name="photo_download"),
    url(r'^%s/download/crop/(?P<id>\d+)/(?P<size>\d+x\d+)/$' % urlpath, 'photos.views.photo_size', kwargs={'download':True,'crop':True}, name="photo_crop_download"),

    ## dynamic photo size ##

    url(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/$' % urlpath, 'photos.views.photo_size', name="photo.size"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>[crop]*)/$' % urlpath, 'photos.views.photo_size', name="photo.size"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<constrain>[constrain]*)/$' % urlpath, 'photos.views.photo_size', name="photo.size"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>[crop]*)/(?P<quality>\d+)/$' % urlpath, 'photos.views.photo_size', name="photo.size"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<constrain>[constrain]*)/(?P<quality>\d+)/$' % urlpath, 'photos.views.photo_size', name="photo.size"),
)
