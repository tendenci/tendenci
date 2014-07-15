import os

from django import forms
from django.template.defaultfilters import slugify
from django.conf import settings

from tendenci.addons.locations.utils import csv_to_dict


class UploadForm(forms.Form):
    """
    CSV upload form for locations imports
    """

    csv = forms.FileField(label='')


class ImportMapForm(forms.Form):

    def __init__(self, *args, **kwargs):

        locport = kwargs.pop('locport')
        super(ImportMapForm, self).__init__(*args, **kwargs)

        #file_path = os.path.join(settings.MEDIA_ROOT, locport.get_file().file.name)
        file_path = str(locport.get_file().file.name)
        csv = csv_to_dict(file_path)

        # choices list
        choices = csv[0].keys()
        machine_choices = [slugify(c).replace('-','') for c in choices]
        choice_tuples = zip(machine_choices, choices)

        choice_tuples.insert(0, ('',''))  # insert blank option; top option
        choice_tuples = sorted(choice_tuples, key=lambda c: c[0].lower())

        native_fields = [
            'Location Name',
            'Description',
            'Contact',
            'Address',
            'Address 2',
            'City',
            'State',
            'Zipcode',
            'Country',
            'Phone',
            'Fax',
            'Email',
            'Website',
            'Latitude',
            'Longitude',
            'Headquarters',
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

