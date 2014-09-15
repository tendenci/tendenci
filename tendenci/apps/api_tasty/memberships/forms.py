from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from tendenci.addons.memberships.models import MembershipDefault
from tendenci.core.api_tasty.forms import TendenciForm

class MembershipForm(TendenciForm):
    create_user = forms.BooleanField(required=False)
    username = forms.CharField(required=False)
    password = forms.CharField(required=False)

    class Meta:
        model = MembershipDefault
        exclude = ('user', 'guid')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MembershipForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = self.cleaned_data
        if data['create_user']:
            username = data.get('username', None)
            password = data.get('password', None)
            if not (username and password):
                raise forms.ValidationError(_("username and password are required to create a user"))
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError(_('username already taken'))
        else:
            username = data.get('username', None)
            if not username:
                raise forms.ValidationError(_("username required if not creating a user"))
            else:
                if not User.objects.filter(username=username).exists():
                    raise forms.ValidationError(_("username does not belong to any user"))
        return data
