from django import forms
from actions.models import Action

class ActionSLAForm(forms.ModelForm):
    sla = forms.BooleanField(required=True, 
                             error_messages={'required': 'The Software License Agreement is Required to Proceed.'})
    class Meta:
        model = Action
        fields = ('sla',)
        
class ActionStep5Form(forms.Form):
    add_article = forms.BooleanField(required=False)
    send_email = forms.BooleanField(required=True,
                             error_messages={'required': 'You must check the "send email" checkbox to send.'})
    
        