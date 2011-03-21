from django.conf.urls.defaults import patterns, url
from events.feeds import LatestEntriesFeed

urlpatterns = patterns('events',                  
    url(r'^$', 'views.index', name="events"),
    url(r'^month/$', 'views.month_view', name="event.month"),
    url(r'^search/$', 'views.search', name="event.search"),
    url(r'^ics/$', 'views.icalendar', name="event.ics"),
    url(r'^print-view/(?P<id>\d+)/$', 'views.print_view', name="event.print_view"),
    url(r'^add/$', 'views.add', name="event.add"),
    url(r'^edit/(?P<id>\d+)/$', 'views.edit', name="event.edit"),
    url(r'^edit/meta/(?P<id>\d+)/$', 'views.edit_meta', name="event.edit.meta"),
    url(r'^delete/(?P<id>\d+)/$', 'views.delete', name="event.delete"),
    url(r'^feed/$', LatestEntriesFeed(), name='event.feed'),
    url(r'^(?P<id>\d+)/$', 'views.index', name="event"),

    # registration confirmation
    url(r'^(?P<id>\d+)/registrations/(?P<reg8n_id>\d+)/$', 
        'views.registration_confirmation', name='event.registration_confirmation'),
    url(r'^(?P<id>\d+)/registrations/(?P<hash>\w+)/$', 
        'views.registration_confirmation', name='event.registration_confirmation'),

    # month-view(s) / day-view
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'views.day_view', name='event.day'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'views.month_view', name='event.month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<type>[\w\-\/]+)/$', 'views.month_view', name='event.month'),

    # register for event
    url(r'^(?P<event_id>\d+)/register/$', 'views.register', name='event.register'),
    url(r'^(?P<event_id>\d+)/multi-register/$', 'views.multi_register', name='event.multi_register'),
    url(r'^registration/(?P<reg8n_id>\d+)/edit/$', 'views.registration_edit', 
        name="event.registration_edit"),
    url(r'^registration/(?P<reg8n_id>\d+)/edit/(?P<hash>\w+)/$', 'views.registration_edit', 
        name="event.registration_edit"),

    # cancel event registration
    url(r'^(?P<event_id>\d+)/registrations/cancel/(?P<registrant_id>\d+)/$', 
        'views.cancel_registration', name='event.cancel_registration'),
    url(r'^(?P<event_id>\d+)/registrations/cancel/(?P<hash>\w+)/$',
        'views.cancel_registration', name='event.cancel_registration'),

    url(r'^types/$', 'views.types', name='event.types'),

    # registrants (search/view); admin-only
    url(r'^(?P<event_id>\d+)/registrants/search/$', 'views.registrant_search', name="event.registrant.search"),

    url(r'^(?P<event_id>\d+)/registrants/roster/$', 'views.registrant_roster', name="event.registrant.roster"),

    url(r'^(?P<event_id>\d+)/registrants/roster/paid',
        'views.registrant_roster',
        {'roster_view':'paid'},
        name="event.registrant.roster.paid"
    ),
    url(r'^(?P<event_id>\d+)/registrants/roster/non-paid',
        'views.registrant_roster',
        {'roster_view':'non-paid'},
        name="event.registrant.roster.non_paid"
    ),
    url(r'^(?P<event_id>\d+)/registrants/roster/total',
        'views.registrant_roster',
        {'roster_view':'total'},
        name="event.registrant.roster.total"
    ),

    # registrant export
    url(r'^(?P<event_id>\d+)/registrants/export/$',
        'views.registrant_export',
        name="event.registrant.export"
    ),
    url(r'^(?P<event_id>\d+)/registrants/export/paid$',
        'views.registrant_export',
        {'roster_view':'paid'},
        name="event.registrant.export.paid"
    ),
    url(r'^(?P<event_id>\d+)/registrants/export/non-paid',
        'views.registrant_export',
        {'roster_view':'non-paid'},
        name="event.registrant.export.non_paid"
    ),
    url(r'^(?P<event_id>\d+)/registrants/export/total',
        'views.registrant_export',
        {'roster_view':'total'},
        name="event.registrant.export.total"
    ),

    url(r'^registrants/(?P<id>\d+)/$', 'views.registrant_details', name="event.registrant"),

    # email registrants
    url(r'^message/(?P<event_id>\d+)/$', 'views.message_add', name='event.message'),

    # event types
    url(r'^(?P<type>[\w\-\/]+)/$', 'views.month_view', name='event.month'),
)