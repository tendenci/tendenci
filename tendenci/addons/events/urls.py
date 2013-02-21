from django.conf.urls.defaults import patterns, url
from tendenci.addons.events.feeds import LatestEntriesFeed

urlpatterns = patterns('tendenci.addons.events',
    url(r'^$', 'views.month_redirect', name="events"),
    url(r'^month/$', 'views.month_view', name="event.month"),
    url(r'^today/$', 'views.today_redirect', name="event.today"),
    url(r'^search/$', 'views.search', name="event.search"),
    url(r'^ics/$', 'views.icalendar', name="event.ics"),
    url(r'^print-view/(?P<id>\d+)/$', 'views.print_view', name="event.print_view"),
    url(r'^add/$', 'views.add', name="event.add"),
    url(r'^export/$', 'views.export', name="event.export"),
    url(r'^import/add/$', 'views.import_add', name='event.import_add'),
    url(r'^import/preview/(?P<import_id>\d+)/$', 'views.import_preview', name='event.import_preview'),
    url(r'^import/process/(?P<import_id>\d+)/$', 'views.import_process', name='event.import_process'),
    url(r'^import/download_template/$', 'views.download_template_csv', name='event.download_template_csv'),
    url(r'^create_ics/$', 'views.create_ics', name="event.create_ics"),
    url(r'^myevents/$', 'views.myevents', name="event.myevents"),
    url(r'^get_place$', 'views.get_place', name="event.get_place"),

    url(r'^add/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'views.add', name="event.add"),

    url(r'^edit/(?P<id>\d+)/$', 'views.edit', name="event.edit"),
    url(r'^copy/(?P<id>\d+)/$', 'views.copy', name="event.copy"),
    url(r'^edit/meta/(?P<id>\d+)/$', 'views.edit_meta', name="event.edit.meta"),
    url(r'^edit/email/(?P<event_id>\d+)/$', 'views.edit_email', name="event.edit.email"),
    url(r'^delete/(?P<id>\d+)/$', 'views.delete', name="event.delete"),
    url(r'^ics/(?P<id>\d+)/$', 'views.icalendar_single', name="event.ics_single"),
    url(r'^feed/$', LatestEntriesFeed(), name='event.feed'),
    url(r'^(?P<id>\d+)/$', 'views.details', name="event"),

    url(r'^(?P<event_id>\d+)/attendees$', 'views.view_attendees', name="event.attendees"),
    
    #delete
    url(r'^speaker/(?P<id>\d+)/delete/$', 'views.delete_speaker', name='event.delete_speaker'),
    url(r'^group_pricing/(?P<id>\d+)/delete/$', 'views.delete_group_pricing', name='event.delete_group_pricing'),
    url(r'^special_pricing/(?P<id>\d+)/delete/$', 'views.delete_special_pricing', name='event.delete_special_pricing'),

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
    url(r'^register/(?P<event_id>\d+)/$', 'views.register', name='event.register'),
    url(r'^register/(?P<event_id>\d+)/pre/$', 'views.register_pre', name='event.register_pre'),
    url(r'^register/(?P<event_id>\d+)/individual/(?P<pricing_id>\d+)/$', 'views.register', {'individual': True}, name='event.register_individual'),
    url(r'^register/(?P<event_id>\d+)/table/(?P<pricing_id>\d+)/$', 'views.register', {'is_table': True}, name='event.register_table'),
#    url(r'^(?P<event_id>\d+)/multi-register/$', 'views.register', name='event.register'),
    url(r'^registration/(?P<reg8n_id>\d+)/edit/$', 'views.registration_edit', 
        name="event.registration_edit"),
    url(r'^registration/(?P<reg8n_id>\d+)/edit/(?P<hash>\w+)/$', 'views.registration_edit', 
        name="event.registration_edit"),
    url(r'^registrant/checkin/', 'views.registrant_check_in', name='event.registrant_check_in'),

    # cancel event registration
    url(r'^(?P<event_id>\d+)/registrants/cancel/(?P<registrant_id>\d+)/$', 
        'views.cancel_registrant', name='event.cancel_registrant'),
    url(r'^(?P<event_id>\d+)/registrants/cancel/(?P<hash>\w+)/$',
        'views.cancel_registrant', name='event.cancel_registrant'),

    url(r'^(?P<event_id>\d+)/registrations/cancel/(?P<registration_id>\d+)/$', 
        'views.cancel_registration', name='event.cancel_registration'),
    url(r'^(?P<event_id>\d+)/registrations/cancel/(?P<registration_id>\d+)/(?P<hash>\w+)/$',
        'views.cancel_registration', name='event.cancel_registration'),

    url(r'^types/$', 'views.types', name='event.types'),
    url(r'^reassign_type/(?P<type_id>\d+)$', 'views.reassign_type', name='event.reassign_type'),

    # registrants (search/view); admin-only
    url(r'^registrants/search/$', 'views.global_registrant_search', name="event.global.registrant.search"),
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
        'views.registrant_export_with_custom',
        name="event.registrant.export"
    ),
    url(r'^(?P<event_id>\d+)/registrants/export/paid$',
        'views.registrant_export_with_custom',
        {'roster_view':'paid'},
        name="event.registrant.export.paid"
    ),
    url(r'^(?P<event_id>\d+)/registrants/export/non-paid',
        'views.registrant_export_with_custom',
        {'roster_view':'non-paid'},
        name="event.registrant.export.non_paid"
    ),
    url(r'^(?P<event_id>\d+)/registrants/export/total',
        'views.registrant_export_with_custom',
        {'roster_view':'total'},
        name="event.registrant.export.total"
    ),
    
#    # dynamic pricing registration
#    url(r'^(?P<event_id>\d+)/register/$', 'registration.views.multi_register', name='event.anon_multi_register'),
#    url(r'^(?P<event_id>\d+)/register/pricing/$', 'registration.views.ajax_pricing', name='event.reg_pricing'),
#    url(r'^(?P<event_id>\d+)/register/user_status/$', 'registration.views.ajax_user', name='event.reg_user_status'),
    
    # addons
    url(r'^(?P<event_id>\d+)/addons/$', 'views.list_addons', name='event.list_addons'),
    url(r'^(?P<event_id>\d+)/addons/add/$', 'views.add_addon', name='event.add_addon'),
    url(r'^(?P<event_id>\d+)/addons/(?P<addon_id>\d+)/edit/$', 'views.edit_addon', name='event.edit_addon'),
    url(r'^(?P<event_id>\d+)/addons/(?P<addon_id>\d+)/disable/$', 'views.disable_addon', name='event.disable_addon'),
    url(r'^(?P<event_id>\d+)/addons/(?P<addon_id>\d+)/enable/$', 'views.enable_addon', name='event.enable_addon'),
    
    # pending events
    url(r'^minimal_add/$', 'views.minimal_add', name='event.minimal_add'),
    url(r'^pending/$', 'views.pending', name='event.pending'),
    url(r'^pending/(?P<event_id>\d+)/approve/$', 'views.approve', name='event.approve'),
    
    url(r'^registrants/(?P<id>\d+)/$', 'views.registrant_details', name="event.registrant"),
    
    # email registrants
    url(r'^message/(?P<event_id>\d+)/$', 'views.message_add', name='event.message'),
    
    # custom registration form preview
    url(r'^custom_reg_form/preview/(?P<id>\d+)/$', 'views.custom_reg_form_preview', 
        name='event.custom_reg_form_preview'),
    # custom registration form preview
    url(r'^custom_reg_form/list/(?P<event_id>\d+)/$', 'views.event_custom_reg_form_list', 
        name='event.event_custom_reg_form_list'),
    
    # event types, need to be the last in the urls
    url(r'^(?P<type>[\w\-\/]+)/$', 'views.month_view', name='event.month'),
    
)
