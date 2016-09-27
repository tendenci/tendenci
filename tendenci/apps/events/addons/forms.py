from django import forms
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.events.models import RegAddon, RegAddonOption

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
        self.chosen_addon = None
        super(RegAddonForm, self).__init__(*args, **kwargs)

        # initialize addon options and reg_set field
        self.fields['addon'] = forms.ModelChoiceField(
            queryset=self.addons,
            widget=forms.TextInput(attrs={'class': 'addon-input'}))

        # dynamically create an option field for each addon
        for addon in self.addons:
            field_name = addon.field_name()
            self.fields[field_name] = forms.ModelChoiceField(
                label=_("Options"), required=False, empty_label=None,
                queryset=addon.options.all(),
                widget=forms.HiddenInput(attrs={'class': 'option-hidden'}))

    def get_form_label(self):
        return self.form_index + 1

    def clean_addon(self):
        addon = self.cleaned_data['addon']
        self.chosen_addon = addon
        if addon not in self.valid_addons:
            raise forms.ValidationError(_('Addon is invalid for current set of registrants'))
        return addon

    def clean(self):
        """Validate the option fields for the selected addon only"""
        data = self.cleaned_data
        if 'addon' in data:
            addon = data['addon']
            option = data[addon.field_name()]
            if not option:
                raise forms.ValidationError(_('Option required for %s' % (addon.title)))

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
            option = data[addon.field_name()]
            RegAddonOption.objects.create(
                option = option,
                regaddon = regaddon,
            )
            return regaddon
        return None
