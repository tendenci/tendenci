from django import forms
from django.utils.translation import ugettext_lazy as _
from tendenci.core.email_blocks.models import EmailBlock

class EmailBlockForm(forms.ModelForm):
    STATUS_CHOICES = (('active',_('Active')),('inactive',_('Inactive')),)
    email = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'size':'45'}))
    email_domain = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'size':'45'}))
    reason =forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'rows':'3'}))
    status_detail = forms.ChoiceField(choices=STATUS_CHOICES)

    class Meta:
        model = EmailBlock
        fields = ('email',
                  'email_domain',
                  'reason',
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

        return super(EmailBlockForm, self).save(*args, **kwargs)
