import re

from decimal import Decimal

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, AnonymousUser

from captcha.fields import CaptchaField
from discounts.models import Discount
from perms.utils import is_admin
from site_settings.utils import get_setting

from events.models import Addon, AddonOption, RegAddon, RegAddonOption

class RegAddonForm(forms.Form):
    """RegAddon form during registration.
    The choices for the addon will depend on the registrants.
    Before this form can be validated the registrant formset must to be
    validated first.
    The valid_addons kwarg is the list of addons that the registrants are allowed to use.
    A RegAddonForm will dynamically add choice fields depending on the
    number of options it has.
    """
    
    def __init__(self, *args, **kwargs):
        self.addons = kwargs.pop('addons')
        self.valid_addons = kwargs.pop('valid_addons', [])
        self.form_index = kwargs.pop('form_index', None)
        super(RegAddonForm, self).__init__(*args, **kwargs)
        
        # initialize addon options and reg_set field
        self.fields['addon'] = forms.ModelChoiceField(
            queryset=self.addons,
            widget=forms.TextInput(attrs={'class': 'addon-input'}))
        
        # dynamically create a field for all the possible options
        for option in AddonOption.objects.filter(addon__in=self.addons):
            field_name = option.field_name()
            choices = [(op, op) for op in option.choice_list()]
            self.fields[field_name] = forms.ChoiceField(
                choices=choices, label=_(option.title), required=False)
        
    def get_form_label(self):
        return self.form_index + 1
        
    def clean_addon(self):
        addon = self.cleaned_data['addon']
        if addon not in self.valid_addons:
            raise forms.ValidationError(_('Addon is invalid for current set of registrants'))
        return addon
            
    def clean(self):
        """Validate the option fields for the selected addon only"""
        data = self.cleaned_data
        if 'addon' in data:
            addon = data['addon']
            for option in addon.options.all():
                try:
                    data[option.field_name()]
                except KeyError:
                    raise forms.ValidationError(_('%s is a required option for %s' % (option.title, addon.title)))
        return data
    
    def save(self, registration):
        if self.is_valid():
            data = self.cleaned_data
            addon = data['addon']
            regaddon = RegAddon.objects.create(
                registration=registration,
                addon=addon,
                amount=addon.price,
            )
            for option in addon.options.all():
                RegAddonOption.objects.create(
                    selected_option = data[option.field_name()],
                    option = option,
                    regaddon = regaddon,
                )
            return regaddon
        return None
