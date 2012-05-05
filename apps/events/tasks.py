import os
from django.forms.models import model_to_dict
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.contrib.contenttypes import generic
from django.forms.models import model_to_dict
from celery.task import Task
from celery.registry import tasks
from imports.utils import render_excel
from events.models import Event

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
            'private',
            'password',
            'on_weekend',
            'external_url',
            'image',
            'tags',
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
            'user',
            'name',
            'description',
        ]
        organizer_fields = [
            'event',
            'user',
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
        
        events = Event.objects.filter(status=1)
        file_name = 'events.xls'
        data_row_list = []
        
        for event in events:
            data_row = []
            
            # event setup
            event_d = model_to_dict(event)
            for field in event_fields:
                value = None
                if field == 'entity':
                    if event.entity:
                        value = event.entity.entity_name
                elif field == 'type':
                    if event.type:
                        value = event.type.name
                else:
                    value = event_d[field]
                value = unicode(value).replace(os.linesep, ' ').rstrip()
                data_row.append(value)
                
            if event.place:
                # place setup
                place_d = model_to_dict(event.place)
                for field in place_fields:
                    value = place_d[field]
                    value = unicode(value).replace(os.linesep, ' ').rstrip()
                    data_row.append(value)
            
            if event.registration_configuration:
                # config setup
                conf_d = model_to_dict(event.registration_configuration)
                for field in configuration_fields:
                    if field == "payment_method":
                        value = event.registration_configuration.payment_method.all()
                    else:
                        value = conf_d[field]
                    value = unicode(value).replace(os.linesep, ' ').rstrip()
                    data_row.append(value)
            
            data_row.append('\n') # append a new line to make a new row
            data_row_list.append(data_row)
        
        fields = event_fields + ["place %s" % f for f in place_fields]
        fields = fields + ["config %s" % f for f in configuration_fields]
        fields.append('\n')
        return render_excel(file_name, fields, data_row_list)
