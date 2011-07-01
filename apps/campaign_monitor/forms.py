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
    
    name = forms.CharField()
    screenshot_file = forms.FileField()
    html_file = forms.FileField()
    zip_file = forms.FileField()
    
    
class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        
    name = forms.CharField()
    subject =  forms.CharField()
    from_name = forms.CharField()
    from_email = forms.EmailField()
    reply_to = forms.EmailField()
    template = forms.ModelChoiceField(queryset=Template.objects.all())
    lists = forms.ModelMultipleChoiceField(queryset=ListMap.objects.all())
        
    def clean(self):
        super(CampaignForm, self).clean()
        data = self.cleaned_data
        
        lists = data.get('lists', None)
        if lists:
            list_ids = [list.list_id for list in lists]
        else:
            list_ids = []
        subject = data.get('subject', None)
        name = data.get('name', None)
        from_name = data.get('from_name', None)
        from_email = data.get('from_email', None)
        reply_to = data.get('reply_to', None)
        template = data.get('template', None)
        
        if lists and subject and name and from_name and from_email and reply_to and template:
            try:
                CSC.create(client_id, subject, name, from_name, from_email, 
                    reply_to, template.html_url, template.template_url,
                    list_ids,[])
            except Exception, e:
                raise forms.ValidationError(e)
        
        return data
