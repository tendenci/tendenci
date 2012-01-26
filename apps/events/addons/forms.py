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
    A RegAddonForm will dynamically add choice fields depending on the
    number of options it has.
    """
    
    def __init__(self, *args, **kwargs):
        self.addons = kwargs.pop('addons')
        self.form_index = kwargs.pop('form_index', None)
        super(RegAddonForm, self).__init__(*args, **kwargs)
        
        # initialize addon options and reg_set field
        self.fields['addon'] = forms.ModelChoiceField(queryset=self.addons)
        
        # dynamically create a field for all the possible options
        for option in AddonOption.objects.filter(addon__in=self.addons):
            field_name = '%s_%s'%(option.addon.pk, option.title.replace(' ', ''))
            choices = [('', '---------'),]
            for op in option.choices.split(','):
                if op:
                    choices.append((op, op))
            self.fields[field_name] = forms.ChoiceField(
                choices=choices, required=False)
                
        print self.fields
        
    def get_form_label(self):
        return self.form_index + 1
