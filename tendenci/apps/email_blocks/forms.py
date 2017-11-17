from django import forms
from django.utils.translation import ugettext_lazy as _
from tendenci.apps.email_blocks.models import EmailBlock
from tendenci.apps.perms.forms import TendenciBaseForm

class EmailBlockForm(TendenciBaseForm):
    STATUS_CHOICES = (('active',_('Active')),('inactive',_('Inactive')),)
    email = forms.CharField(max_length=255,
                            required=False,
                            widget=forms.TextInput(attrs={'size':'45'}),
                            help_text=_("Email you wish to block"))
    email_domain = forms.CharField(max_length=255,
                                   required=False,
                                   label='Email domain',
                                   widget=forms.TextInput(attrs={'size':'45'}),
                                   help_text=_("Domain you wish to block"))
    reason =forms.CharField(max_length=255,
                            required=False,
                            widget=forms.Textarea(attrs={'rows':'3'}),
                            help_text=_('The reason why you want to block the email or domain specified above'))
    status_detail = forms.ChoiceField(choices=STATUS_CHOICES)

    class Meta:
        model = EmailBlock
        fields = ('email',
                  'email_domain',
                  'reason',
                  'status_detail',
                  )

    def clean(self):
        email = self.cleaned_data.get('email', None)
        email_domain = self.cleaned_data.get('email_domain', None)
        if not any([email, email_domain]):
            raise forms.ValidationError(_("You'll need to specify either email or email domain."))
