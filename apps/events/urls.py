from django.conf.urls.defaults import patterns, url
from events.feeds import LatestEntriesFeed

urlpatterns = patterns('events',                  
    url(r'^$', 'views.index', name="events"),
    url(r'^search/$', 'views.search', name="event.search"),
    url(r'^print-view/(?P<id>\d+)/$', 'views.print_view', name="event.print_view"),
    url(r'^add/$', 'views.add', name="event.add"),
    url(r'^edit/(?P<id>\d+)/$', 'views.edit', name="event.edit"),
    url(r'^edit/meta/(?P<id>\d+)/$', 'views.edit_meta', name="event.edit.meta"),
    url(r'^delete/(?P<id>\d+)/$', 'views.delete', name="event.delete"),
    url(r'^feed/$', LatestEntriesFeed(), name='event.feed'),
    url(r'^(?P<id>\d+)/$', 'views.index', name="event"),

    # month-view / day-view
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'views.month_view', name='event.month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'views.day_view', name='event.day'),

    # register for event
    url(r'^(?P<event_id>\d+)/register/$', 'views.register', name='event.register'),
    url(r'^(?P<event_id>\d+)/register/confirm/$', 'views.register_confirm', name='event.register.confirm'),

    # registrants (search/view); admin-only
    url(r'^(?P<event_id>\d+)/registrants/search/$', 'views.registrant_search', name="event.registrant.search"),
    url(r'^registrants/(?P<id>\d+)/$', 'views.registrant_details', name="event.registrant"),

    url(r'^edit/place/(?P<id>\d+)/$', 'views.edit_place', name="event.edit.place"),
    url(r'^edit/sponsors/(?P<id>\d+)/$', 'views.edit_sponsor', name="event.edit.sponsor"),
    url(r'^edit/speakers/(?P<id>\d+)/$', 'views.edit_speaker', name="event.edit.speaker"),
    url(r'^edit/organizers/(?P<id>\d+)/$', 'views.edit_organizer', name="event.edit.organizer"),
    url(r'^(?P<event_id>\d+)/edit/registration/$', 'views.edit_registration', name="event.edit.registration"),
)