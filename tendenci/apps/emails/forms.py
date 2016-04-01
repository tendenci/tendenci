from django import forms
from tendenci.apps.emails.models import Email
from django.utils.translation import ugettext_lazy as _
from tendenci.libs.tinymce.widgets import TinyMCE

class EmailForm(forms.ModelForm):
    STATUS_CHOICES = (('active',_('Active')),('inactive',_('Inactive')),)
    subject = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size':'50'}))
    recipient =forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'rows':'3'}))
    status_detail = forms.ChoiceField(choices=STATUS_CHOICES)

    body = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style': 'width:80%'},
        mce_attrs={'storme_app_label': Email._meta.app_label,
        'storme_model': Email._meta.model_name.lower()}))

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

    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0
        # add form-control class
        for k in self.fields.keys():
            self.fields[k].widget.attrs['class'] = 'form-control'

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
