from tendenci.apps.careers.models import Career
from tendenci.apps.perms.forms import TendenciBaseForm
from django import forms
from django.utils.translation import gettext_lazy as _

from tendenci.apps.site_settings.utils import get_setting

class CareerForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(
        choices=(('active', _('Active')),
                 ('inactive', _('Inactive')),
                 ('pending', _('Pending')),))

    class Meta:
        model = Career
        fields = (
        'user',
        'company',
        'company_description',
        'sec',
        'level',
        'annual_salary',
        'salary_increase',
        'position_title',
        'position_description',
        'position_type',
        'start_dt',
        'end_dt',
        'experience',
        'allow_anonymous_view',
        'user_perms',
        'member_perms',
        'group_perms',
        'status_detail',
        )

        fieldsets = [(_('Career Information'), {
                      'fields': ['user',
                                'company',
                                'company_description',
                                'sec',
                                'level',
                                'annual_salary',
                                'salary_increase',
                                'position_title',
                                'position_description',
                                'position_type',
                                'start_dt',
                                'end_dt',
                                'experience',
                                 ],
                      }),
                      (_('Permissions'), {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     (_('Administrator Only'), {
                      'fields': ['status_detail'],
                      'classes': ['admin-only'],
                    })]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # sec placeholder
        self.fields['sec'].widget.attrs.update({'placeholder': 'Section'})

        # level choices
        level_options = get_setting('module', 'careers', 'leveloptions').strip()
        if level_options:
            level_options = [item.strip() for item in level_options.split(',')]
            level_choices = [('', '---------')] + list(zip(level_options, level_options))
            #self.fields['level'].choices = level_choices
            self.fields['level'] = forms.ChoiceField(required=False,
                                        choices=level_choices)

        #position_title label
        position_title_label = get_setting('module', 'careers', 'positiontitlelabel')
        if position_title_label:
            self.fields['position_title'].label = position_title_label

        #position_description label
        position_desc_label = get_setting('module', 'careers', 'positiondesclabel')
        if position_desc_label:
            self.fields['position_description'].label = position_desc_label


        # position_type choices
        position_type_options = get_setting('module', 'careers', 'positiontypeoptions').strip()
        if position_type_options:
            position_type_options = [item.strip() for item in position_type_options.split(',')]
            position_type_choices = [('', '---------')] + list(zip(position_type_options, position_type_options))
            self.fields['position_type'] = forms.ChoiceField(required=False,
                                        choices=position_type_choices)
        else:
            self.fields['position_type'] = forms.ChoiceField(required=False,
                                        choices=Career.POSITION_TYPE_CHOICES)
            
            
        #position_type label
        position_type_label = get_setting('module', 'careers', 'positiontypelabel')
        if position_type_label:
            self.fields['position_type'].label = position_type_label

        # check required fields
        required_fields = get_setting('module', 'careers', 'requiredfields')
        if required_fields:
            required_fields_list = [('', '---------')] + [field.strip() for field in required_fields.split(',') if field.strip()]
            for field_name in required_fields_list:
                if field_name in self.fields:
                    self.fields[field_name].required = True
