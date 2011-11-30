import os

from django import forms
from django.forms.widgets import HiddenInput
from django.template.defaultfilters import slugify
from django.conf import settings

from memberships.utils import csv_to_dict
from memberships.models import AppField, App

class UploadForm(forms.Form):
    """
    CSV upload form for membership imports
    """
    
    app = forms.ModelChoiceField(label='Application', queryset=App.objects.all())
    csv = forms.FileField(label="CSV File")
    
    
class ImportMapForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        memport = kwargs.pop('memport')
        super(ImportMapForm, self).__init__(*args, **kwargs)
        
        app = memport.app
        file_path = os.path.join(settings.MEDIA_ROOT, memport.get_file().file.name)
        
        csv = csv_to_dict(file_path)
        
        # choices list
        choices = csv[0].keys()
        
        # make tuples; sort tuples (case-insensitive)
        choice_tuples = [(c,c) for c in csv[0].keys()]
        
        choice_tuples.insert(0, ('',''))  # insert blank option
        choice_tuples = sorted(choice_tuples, key=lambda c: c[0].lower())
        
        app_fields = AppField.objects.filter(app=app)
        
        native_fields = [
            'User Name',
            'Membership Type',
            'Corp. Membership Name',
            'Member Number',
            'Payment Method',
            'Join Date',
            'Renew Date',
            'Expire Date',
            'Owner',
            'Creator',
            'Status',
            'Status Detail',
        ]

        for native_field in native_fields:
            self.fields[slugify(native_field)] = forms.ChoiceField(**{
                'label': native_field,
                'choices': choice_tuples,
                'required': False,
            })

            # compare required field with choices
            # if they match; set initial
            if native_field in choices:
                self.fields[slugify(native_field)].initial = native_field

        self.fields['user-name'].required = True
        self.fields['membership-type'].required = True

        for app_field in app_fields:
            for csv_row in csv:
            
                if slugify(app_field.label) == 'membership-type':
                    continue  # skip membership type

                self.fields[app_field.field_name] = forms.ChoiceField(**{
                    'label':app_field.label,
                    'choices': choice_tuples,
                    'required': False,
                })
                
                # compare label with choices
                # if label matches choice; set initial
                if app_field.label in choices:
                    self.fields[app_field.field_name].initial = app_field.label
