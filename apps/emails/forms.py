from django import forms
from emails.models import Email

class EmailForm(forms.ModelForm):
    #body = forms.CharField(max_length=10000, widget=forms.TextInput(attrs={'size':'40'}))
    subject = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size':'50'}))
    recipient =forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'rows':'3'}))
    
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
                  )
    def save(self, user=None, *args, **kwargs):
        if user and user.id:
            if not self.instance.id:
                self.instance.creator = user
                self.instance.creator_username = user.username
            self.instance.owner = user
            self.instance.owner_username = user.username
            
        return super(EmailForm, self).save(*args, **kwargs)
        