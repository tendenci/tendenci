from builtins import str
import os
from django.db.models import Max, Count
from django.http import HttpResponse
from celery.task import Task
from tendenci.apps.events.ics.utils import create_ics
from tendenci.apps.exports.utils import full_model_to_dict, render_csv
from tendenci.apps.events.models import Event
from tendenci.apps.base.utils import escape_csv

class EventsExportTask(Task):
    """Export Task for Celery
    This exports all events data and registration configuration.
    This export needs to be able to handle additional columns for each
    instance of Pricing, Speaker, and Addon.
    This export does not include registrant data.
    """

    def run(self, **kwargs):
        """Create the xls file"""
        event_fields = [
            'entity',
            'type',
            'title',
            'description',
            'all_day',
            'start_dt',
            'end_dt',
            'timezone',
            'private_slug',
            'password',
            'on_weekend',
            'external_url',
            'image',
            'tags',
            'allow_anonymous_view',
            'allow_user_view',
            'allow_member_view',
            'allow_user_edit',
            'allow_member_edit',
            'create_dt',
            'update_dt',
            'creator',
            'creator_username',
            'owner',
            'owner_username',
            'status',
            'status_detail',
        ]
        place_fields = [
            'name',
            'description',
            'address',
            'city',
            'state',
            'zip',
            'country',
            'url',
        ]
        configuration_fields = [
            'payment_method',
            'payment_required',
            'limit',
            'enabled',
            'is_guest_price',
            'use_custom_reg_form',
            'reg_form',
            'bind_reg_form_to_conf_only',
        ]
        speaker_fields = [
            'name',
            'description',
        ]
        organizer_fields = [
            'name',
            'description',
        ]
        pricing_fields = [
            'title',
            'quantity',
            'group',
            'price',
            'reg_form',
            'start_dt',
            'end_dt',
            'allow_anonymous',
            'allow_user',
            'allow_member',
            'status',
        ]

        events = Event.objects.filter(status=True)
        max_speakers = events.annotate(num_speakers=Count('speaker')).aggregate(Max('num_speakers'))['num_speakers__max']
        max_organizers = events.annotate(num_organizers=Count('organizer')).aggregate(Max('num_organizers'))['num_organizers__max']
        max_pricings = events.annotate(num_pricings=Count('registration_configuration__regconfpricing')).aggregate(Max('num_pricings'))['num_pricings__max']
        file_name = 'events.csv'
        data_row_list = []

        for event in events:
            data_row = []
            # event setup
            event_d = full_model_to_dict(event, fields=event_fields)
            for field in event_fields:
                value = None
                if field == 'entity':
                    if event.entity:
                        value = event.entity.entity_name
                elif field == 'type':
                    if event.type:
                        value = event.type.name
                elif field in event_d:
                    value = event_d[field]
                value = str(value).replace(os.linesep, ' ').rstrip()
                value = escape_csv(value)
                data_row.append(value)

            if event.place:
                # place setup
                place_d = full_model_to_dict(event.place)
                for field in place_fields:
                    value = place_d[field]
                    value = str(value).replace(os.linesep, ' ').rstrip()
                    value = escape_csv(value)
                    data_row.append(value)

            if event.registration_configuration:
                # config setup
                conf_d = full_model_to_dict(event.registration_configuration)
                for field in configuration_fields:
                    if field == "payment_method":
                        value = event.registration_configuration.payment_method.all()
                    else:
                        value = conf_d[field]
                    value = str(value).replace(os.linesep, ' ').rstrip()
                    value = escape_csv(value)
                    data_row.append(value)

            if event.speaker_set.all():
                # speaker setup
                for speaker in event.speaker_set.all():
                    speaker_d = full_model_to_dict(speaker)
                    for field in speaker_fields:
                        value = speaker_d[field]
                        value = str(value).replace(os.linesep, ' ').rstrip()
                        value = escape_csv(value)
                        data_row.append(value)

            # fill out the rest of the speaker columns
            if event.speaker_set.all().count() < max_speakers:
                for i in range(0, max_speakers - event.speaker_set.all().count()):
                    for field in speaker_fields:
                        data_row.append('')

            if event.organizer_set.all():
                # organizer setup
                for organizer in event.organizer_set.all():
                    organizer_d = full_model_to_dict(organizer)
                    for field in organizer_fields:
                        value = organizer_d[field]
                        value = str(value).replace(os.linesep, ' ').rstrip()
                        value = escape_csv(value)
                        data_row.append(value)

            # fill out the rest of the organizer columns
            if event.organizer_set.all().count() < max_organizers:
                for i in range(0, max_organizers - event.organizer_set.all().count()):
                    for field in organizer_fields:
                        data_row.append('')

            reg_conf = event.registration_configuration
            if reg_conf and reg_conf.regconfpricing_set.all():
                # pricing setup
                for pricing in reg_conf.regconfpricing_set.all():
                    pricing_d = full_model_to_dict(pricing)
                    for field in pricing_fields:
                        value = pricing_d[field]
                        value = str(value).replace(os.linesep, ' ').rstrip()
                        value = escape_csv(value)
                        data_row.append(value)

            # fill out the rest of the pricing columns
            if reg_conf and reg_conf.regconfpricing_set.all().count() < max_pricings:
                for i in range(0, max_pricings - reg_conf.regconfpricing_set.all().count()):
                    for field in pricing_fields:
                        data_row.append('')

            data_row_list.append(data_row)

        fields = event_fields + ["place %s" % f for f in place_fields]
        fields = fields + ["config %s" % f for f in configuration_fields]
        for i in range(0, max_speakers):
            fields = fields + ["speaker %s %s" % (i, f) for f in speaker_fields]
        for i in range(0, max_organizers):
            fields = fields + ["organizer %s %s" % (i, f) for f in organizer_fields]
        for i in range(0, max_pricings):
            fields = fields + ["pricing %s %s" % (i, f) for f in pricing_fields]
        return render_csv(file_name, fields, data_row_list)

class EventsICSTask(Task):
    """ICS precreation task for Celery
    This creates ics file for a specific user.
    """

    def run(self, **kwargs):
        if kwargs.get('ics'):
            ics = kwargs.get('ics')
            ics_str = create_ics(ics.user)
            response = HttpResponse(ics_str)
            response['Content-Type'] = 'text/calendar'
            response['Content-Disposition'] = 'attachment; filename="ics-%s.ics"' % (ics.user.pk)
            return response
