from django import forms
from django.conf import settings
from campaign_monitor.models import Template, Campaign, ListMap
from createsend import CreateSend
from createsend import Campaign as CSC

api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None)
client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
CreateSend.api_key = api_key

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        exclude = ["template_id", "create_date", "update_date", "cm_preview_url", "cm_screenshot_url"]
    
    screenshot_file = forms.FileField(required=False)
    zip_file = forms.FileField(required=False)
    
class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        exclude = ["campaign_id", "status", "sent_date"]
        
    name = forms.CharField()
    subject =  forms.CharField()
    from_name = forms.CharField()
    from_email = forms.EmailField()
    reply_to = forms.EmailField()
    template = forms.ModelChoiceField(queryset=Template.objects.all())
    lists = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=ListMap.objects.all())


