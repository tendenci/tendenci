from django import forms
from tendenci.core.emails.models import Email
from django.utils.translation import ugettext_lazy as _

class EmailForm(forms.ModelForm):
    STATUS_CHOICES = (('active',_('Active')),('inactive',_('Inactive')),)
    subject = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size':'50'}))
    recipient =forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'rows':'3'}))
    status_detail = forms.ChoiceField(choices=STATUS_CHOICES)

    class Meta:
        model = Email
        fields = ('content_type',
                  'subject',
                  'body',
                  'sender',
                  'sender_display',
                  'reply_to',
                  'recipient',
                  'status',
                  'status_detail',
                  )
    def save(self, user=None, *args, **kwargs):
        if user and user.id:
            if not self.instance.id:
                self.instance.creator = user
                self.instance.creator_username = user.username
            self.instance.owner = user
            self.instance.owner_username = user.username

        return super(EmailForm, self).save(*args, **kwargs)

class AmazonSESVerifyEmailForm(forms.Form):
    email_address = forms.EmailField(max_length=255, label=_("Enter an email address to verify"))
