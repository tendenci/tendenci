from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'events', 'url')
if not urlpath:
    urlpath = "events"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.month_redirect, name="events"),
    url(r'^%s/week/$' % urlpath, views.week_view, name="event.week"),
    url(r'^%s/month/$' % urlpath, views.month_view, name="event.month"),
    url(r'^%s/today/$' % urlpath, views.today_redirect, name="event.today"),
    url(r'^%s/search/$' % urlpath, views.search, name="event.search"),
    url(r'^%s/search/past/$' % urlpath, views.search, {'past': True}, name="event.past_search"),
    url(r'^%s/templates/$' % urlpath, views.templates_list, name="event.templates_list"),
    url(r'^%s/ics/$' % urlpath, views.icalendar, name="event.ics"),
    url(r'^%s/print-view/(?P<id>\d+)/$' % urlpath, views.print_view, name="event.print_view"),
    url(r'^%s/add/$' % urlpath, views.add, name="event.add"),
    url(r'^%s/add/template/$' % urlpath, views.add, {'is_template': True}, name="event.add_template"),
    url(r'^%s/import/add/$' % urlpath, views.import_add, name='event.import_add'),
    url(r'^%s/import/preview/(?P<import_id>\d+)/$' % urlpath, views.import_preview, name='event.import_preview'),
    url(r'^%s/import/process/(?P<import_id>\d+)/$' % urlpath, views.import_process, name='event.import_process'),
    url(r'^%s/import/download_template/$' % urlpath, views.download_template_csv, name='event.download_template_csv'),
    url(r'^%s/create_ics/$' % urlpath, views.create_ics, name="event.create_ics"),
    url(r'^%s/myevents/$' % urlpath, views.myevents, name="event.myevents"),
    url(r'^%s/get_place$' % urlpath, views.get_place, name="event.get_place"),

    # events reports
    url(r'^%s/reports/financial/$' % urlpath, views.reports_financial, name='event.reports.financial'),
    url(r'^%s/reports/financial/export_status/(?P<identifier>\d+)$' % urlpath, views.financial_export_status, name='event.reports.financial.export_status'),
    url(r'^%s/reports/financial/download/(?P<identifier>\d+)/$' % urlpath, views.financial_export_download, name='event.reports.financial.export_download'),

    url(r'^%s/add/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$' % urlpath, views.add, name="event.add"),

    url(r'^%s/overview/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="event.edit"),
    url(r'^%s/location/edit/(?P<id>\d+)/$' % urlpath, views.location_edit, name="event.location_edit"),
    url(r'^%s/organizer/edit/(?P<id>\d+)/$' % urlpath, views.organizer_edit, name="event.organizer_edit"),
    url(r'^%s/sponsor/edit/(?P<id>\d+)/$' % urlpath, views.sponsor_edit, name="event.sponsor_edit"),
    url(r'^%s/speakers/edit/(?P<id>\d+)/$' % urlpath, views.speaker_edit, name="event.speaker_edit"),
    url(r'^%s/regconf/edit/(?P<id>\d+)/$' % urlpath, views.regconf_edit, name="event.regconf_edit"),
    url(r'^%s/pricing/edit/(?P<id>\d+)/$' % urlpath, views.pricing_edit, name="event.pricing_edit"),

    url(r'^%s/copy/(?P<id>\d+)/$' % urlpath, views.copy, name="event.copy"),
    url(r'^%s/add-from-template/(?P<id>\d+)/$' % urlpath, views.add_from_template, name="event.add_from_template"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="event.edit.meta"),
    url(r'^%s/edit/email/(?P<event_id>\d+)/$' % urlpath, views.edit_email, name="event.edit.email"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="event.delete"),
    url(r'^%s/delete_recurring/(?P<id>\d+)/$' % urlpath, views.delete_recurring, name="event.delete_recurring"),
    url(r'^%s/ics/(?P<id>\d+)/$' % urlpath, views.icalendar_single, name="event.ics_single"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='event.feed'),
    url(r'^%s/(?P<id>\d+)/$' % urlpath, views.details, name="event"),
    url(r'^%s/recurring/(?P<id>\d+)/$' % urlpath, views.recurring_details, name="event.recurring"),

    # event export
    url(r'^%s/export/$' % urlpath, views.export, name="event.export"),
    url(r'^%s/export/status/(?P<identifier>\d+)/$' % urlpath, views.export_status, name="event.export_status"),
    url(r'^%s/export/download/(?P<identifier>\d+)/$' % urlpath, views.export_download, name="event.export_download"),

    # speakers_list view does not exist
    url(r'^%s/(?P<event_id>\d+)/speakers/$' % urlpath, views.speaker_list, name="event.speakers"),
    url(r'^%s/(?P<event_id>\d+)/attendees$' % urlpath, views.view_attendees, name="event.attendees"),

    #delete
    url(r'^%s/speaker/(?P<id>\d+)/delete/$' % urlpath, views.delete_speaker, name='event.delete_speaker'),
    #url(r'^%s/group_pricing/(?P<id>\d+)/delete/$' % urlpath, views.delete_group_pricing, name='event.delete_group_pricing'),
    #url(r'^%s/special_pricing/(?P<id>\d+)/delete/$' % urlpath, views.delete_special_pricing, name='event.delete_special_pricing'),

    # registration confirmation
    url(r'^%s/(?P<id>\d+)/registrations/(?P<reg8n_id>\d+)/$' % urlpath,
        views.registration_confirmation, name='event.registration_confirmation'),
    url(r'^%s/(?P<id>\d+)/registrations/(?P<hash>\w+)/$' % urlpath,
        views.registration_confirmation, name='event.registration_confirmation'),

    # month-view(s) / day-view
    url(r'^%s/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$' % urlpath, views.day_view, name='event.day'),
    url(r'^%s/week/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$' % urlpath, views.week_view, name='event.week'),
    url(r'^%s/week/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<type>[\w\-\/]+)/$' % urlpath, views.week_view, name='event.week'),
    url(r'^%s/(?P<year>\d{4})/(?P<month>\d{1,2})/$' % urlpath, views.month_view, name='event.month'),
    url(r'^%s/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<type>[\w\-\/]+)/$' % urlpath, views.month_view, name='event.month'),

    # register for event
    url(r'^%s/member-register/(?P<event_id>\d+)/$' % urlpath, views.member_register, name='event.member_register'),
    url(r'^%s/register/(?P<event_id>\d+)/$' % urlpath, views.register, name='event.register'),
    url(r'^%s/register/(?P<event_id>\d+)/pre/$' % urlpath, views.register_pre, name='event.register_pre'),
    url(r'^%s/register/(?P<event_id>\d+)/individual/(?P<pricing_id>\d+)/$' % urlpath, views.register, {'individual': True}, name='event.register_individual'),
    url(r'^%s/register/(?P<event_id>\d+)/table/(?P<pricing_id>\d+)/$' % urlpath, views.register, {'is_table': True}, name='event.register_table'),

    url(r'^%s/registration/(?P<reg8n_id>\d+)/edit/$' % urlpath, views.registration_edit,
        name="event.registration_edit"),
    url(r'^%s/registration/(?P<reg8n_id>\d+)/edit/(?P<hash>\w+)/$' % urlpath, views.registration_edit,
        name="event.registration_edit"),
    url(r'^%s/registrant/checkin/' % urlpath, views.registrant_check_in, name='event.registrant_check_in'),

    # cancel event registration
    url(r'^%s/(?P<event_id>\d+)/registrants/cancel/(?P<registrant_id>\d+)/$' % urlpath,
        views.cancel_registrant, name='event.cancel_registrant'),
    url(r'^%s/(?P<event_id>\d+)/registrants/cancel/(?P<hash>\w+)/$' % urlpath,
        views.cancel_registrant, name='event.cancel_registrant'),

    url(r'^%s/(?P<event_id>\d+)/registrations/cancel/(?P<registration_id>\d+)/$' % urlpath,
        views.cancel_registration, name='event.cancel_registration'),
    url(r'^%s/(?P<event_id>\d+)/registrations/cancel/(?P<registration_id>\d+)/(?P<hash>\w+)/$' % urlpath,
        views.cancel_registration, name='event.cancel_registration'),

    url(r'^%s/types/$' % urlpath, views.types, name='event.types'),
    url(r'^%s/reassign_type/(?P<type_id>\d+)$' % urlpath, views.reassign_type, name='event.reassign_type'),

    # registrants (search/view); admin-only
    url(r'^%s/registrants/search/$' % urlpath, views.global_registrant_search, name="event.global.registrant.search"),
    url(r'^%s/(?P<event_id>\d+)/registrants/search/$' % urlpath, views.registrant_search, name="event.registrant.search"),

    url(r'^%s/(?P<event_id>\d+)/registrants/roster/$' % urlpath,
        views.registrant_roster,
        name="event.registrant.roster"),

    url(r'^%s/(?P<event_id>\d+)/registrants/roster/paid' % urlpath,
        views.registrant_roster,
        {'roster_view': 'paid'},
        name="event.registrant.roster.paid"),
    url(r'^%s/(?P<event_id>\d+)/registrants/roster/non-paid' % urlpath,
        views.registrant_roster,
        {'roster_view': 'non-paid'},
        name="event.registrant.roster.non_paid"),
    url(r'^%s/(?P<event_id>\d+)/registrants/roster/total' % urlpath,
        views.registrant_roster,
        {'roster_view': 'total'},
        name="event.registrant.roster.total"),

    # registrant export
    url(r'^%s/(?P<event_id>\d+)/registrants/export/$' % urlpath,
        views.registrant_export_with_custom,
        name="event.registrant.export"),
    url(r'^%s/(?P<event_id>\d+)/registrants/export/paid$' % urlpath,
        views.registrant_export_with_custom,
        {'roster_view': 'paid'},
        name="event.registrant.export.paid"),
    url(r'^%s/(?P<event_id>\d+)/registrants/export/non-paid' % urlpath,
        views.registrant_export_with_custom,
        {'roster_view': 'non-paid'},
        name="event.registrant.export.non_paid"),
    url(r'^%s/(?P<event_id>\d+)/registrants/export/total' % urlpath,
        views.registrant_export_with_custom,
        {'roster_view': 'total'},
        name="event.registrant.export.total"),

    url(r'^%s/(?P<id>\d+)/(?P<private_slug>\w+)/$' % urlpath, views.details, name='event.private_details'),

    # addons
    url(r'^%s/(?P<event_id>\d+)/addons/list/$' % urlpath, views.list_addons, name='event.list_addons'),
    url(r'^%s/(?P<event_id>\d+)/addons/add/$' % urlpath, views.add_addon, name='event.add_addon'),
    url(r'^%s/(?P<event_id>\d+)/addons/(?P<addon_id>\d+)/edit/$' % urlpath, views.edit_addon, name='event.edit_addon'),
    url(r'^%s/(?P<event_id>\d+)/addons/(?P<addon_id>\d+)/disable/$' % urlpath, views.disable_addon, name='event.disable_addon'),
    url(r'^%s/(?P<event_id>\d+)/addons/(?P<addon_id>\d+)/enable/$' % urlpath, views.enable_addon, name='event.enable_addon'),
    url(r'^%s/(?P<event_id>\d+)/addons/(?P<addon_id>\d+)/delete/$' % urlpath, views.delete_addon, name='event.delete_addon'),

    # pending events
    url(r'^%s/minimal_add/$' % urlpath, views.minimal_add, name='event.minimal_add'),
    url(r'^%s/pending/$' % urlpath, views.pending, name='event.pending'),
    url(r'^%s/pending/(?P<event_id>\d+)/approve/$' % urlpath, views.approve, name='event.approve'),
    url(r'^%s/registrants/(?P<id>\d+)/$' % urlpath, views.registrant_details, name="event.registrant"),

    # email registrants
    url(r'^%s/message/(?P<event_id>\d+)/$' % urlpath, views.message_add, name='event.message'),

    # custom registration form preview
    url(r'^%s/custom_reg_form/preview/(?P<id>\d+)/$' % urlpath, views.custom_reg_form_preview, name='event.custom_reg_form_preview'),
    # custom registration form preview
    url(r'^%s/custom_reg_form/list/(?P<event_id>\d+)/$' % urlpath, views.event_custom_reg_form_list, name='event.event_custom_reg_form_list'),

    # free type
    url(r'^%s/check_free_pass_eligibility/$' % urlpath, views.check_free_pass_eligibility, name='event.check_free_pass_eligibility'),

    # event types, need to be the last in the urls
    url(r'^%s/(?P<type>[\w\-\/]+)/$' % urlpath, views.month_view, name='event.month'),

]
