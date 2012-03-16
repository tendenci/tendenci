import os

from django import forms
from django.forms.widgets import HiddenInput
from django.template.defaultfilters import slugify
from django.conf import settings

from memberships.utils import csv_to_dict
from memberships.models import AppField, App

INTERACTIVE_CHOICES = (
    (1, 'Interactive'),
    (0, 'Not Interactive (no login)'),
)

OVERRIDE_CHOICES = (
    (0, 'Blank Fields'),
    (1, 'All Fields (override)'),
)

KEY_CHOICES = (
    ('email','email'),
    ('first_name,last_name,email','first_name and last_name and email'),
    ('first_name,last_name,phone','first_name and last_name and phone'),
    ('first_name,last_name,company','first_name and last_name and company'),
    ('username','username'),
)

class UploadForm(forms.Form):
    """
    CSV upload form for membership imports
    """
    
    app = forms.ModelChoiceField(label='Application', queryset=App.objects.all())
    interactive = forms.CharField(
        widget=forms.RadioSelect(choices=INTERACTIVE_CHOICES),
        initial=0,)
    override = forms.CharField(
        widget=forms.RadioSelect(choices=OVERRIDE_CHOICES),
        initial=0,)
    key = forms.ChoiceField(
        initial="email", choices=KEY_CHOICES)
    csv = forms.FileField(label='')
    
    
class ImportMapForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        memport = kwargs.pop('memport')
        super(ImportMapForm, self).__init__(*args, **kwargs)
        
        app = memport.app
        file_path = os.path.join(settings.MEDIA_ROOT, memport.get_file().file.name)
        
        csv = csv_to_dict(file_path)

        # choices list
        choices = csv[0].keys()
        machine_choices = [slugify(c).replace('-','') for c in choices]
        choice_tuples = zip(machine_choices, choices)

        choice_tuples.insert(0, ('',''))  # insert blank option; top option
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
            native_field_machine = slugify(native_field).replace('-','')

            self.fields[native_field_machine] = forms.ChoiceField(**{
                'label': native_field,
                'choices': choice_tuples,
                'required': False,
            })

            # compare required field with choices
            # if they match; set initial
            if native_field_machine in machine_choices:
                self.fields[native_field_machine].initial = native_field_machine

        self.fields['username'].required = True
        self.fields['membershiptype'].required = True

        for app_field in app_fields:
            for csv_row in csv:
            
                app_field_machine = slugify(app_field.label).replace('-','')

                if slugify(app_field_machine) == 'membershiptype':
                    continue  # skip membership type

                self.fields[app_field_machine] = forms.ChoiceField(**{
                    'label':app_field.label,
                    'choices': choice_tuples,
                    'required': False,
                })

                # compare label with choices
                # if label matches choice; set initial
                if app_field_machine in machine_choices:
                    self.fields[app_field_machine].initial = app_field_machine
