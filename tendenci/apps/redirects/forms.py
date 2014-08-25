from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.redirects.models import Redirect
from tendenci.core.registry import site

class RedirectForm(forms.ModelForm):

    from_app = forms.ChoiceField(choices=[], required=False,
        help_text=_("You may only redirect from a disabled app. You do not need to enter a From URL if you choose an app. All URLs related to this app will be redirected to the URL you enter in the To URL field."))

    def __init__(self, *args, **kwargs):
        super(RedirectForm, self).__init__(*args, **kwargs)
        app_choices = [('', '------')]
        for app in site.get_registered_apps().core:
            if not app.get('enabled'):
                app_choices.append((app, app))
        self.fields['from_app'].choices = app_choices

    def clean_from_app(self):
        value = self.cleaned_data['from_app']
        if value:
            try:
                exists = Redirect.objects.get(from_app = value)
                if exists.pk != self.instance.pk:
                    raise forms.ValidationError(_("Redirect for this app already exists."))
            except Redirect.DoesNotExist:
                pass
        return value

    def clean_from_url(self):
        value = self.cleaned_data['from_url']
        value = value.strip('/')
        if value:
            try:
                exists = Redirect.objects.get(from_url = value)
                if exists.pk != self.instance.pk:
                    raise forms.ValidationError(_("Redirect for this url already exists."))
            except Redirect.DoesNotExist:
                pass
        return value

    def clean_to_url(self):
        value = self.cleaned_data['to_url']
        value = value.strip('/')
        return value

    def clean(self):
        cleaned_data = self.cleaned_data
        from_app = cleaned_data.get('from_app')
        from_url = cleaned_data.get('from_url')
        if not from_app and not from_url:
            raise forms.ValidationError(_("Specify from where the redirect would come from."))
        return cleaned_data

    class Meta:
        model = Redirect
