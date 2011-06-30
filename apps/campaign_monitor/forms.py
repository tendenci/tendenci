from django import forms
from django.conf import settings
from campaign_monitor.models import Template, Campaign, ListMap
from createsend import CreateSend
from createsend import Campaign as CSC
from createsend import Template as CST

api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None) 
client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
CreateSend.api_key = api_key

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
    
    name = forms.CharField()
    preview_url = forms.URLField()
    screenshot_url = forms.URLField()
    html_url = forms.URLField()
    zip_url = forms.URLField()
    
    def clean(self):
        super(TemplateForm, self).clean()
        data = self.cleaned_data
        
        name = data.get('name', None)
        html_url = data.get('html_url', None)
        zip_url = data.get('zip_url', None)
        screenshot_url = data.get('screenshot_url', None)
        
        if name and html_url and zip_url and screenshot_url:
            try:
                if self.instance:
                    CST(template_id = self.instance.template_id)
                    CST.update(name, html_url, zip_url, screenshot_url)
                else:
                    CST.create(client_id, name, html_url, zip_url, screenshot_url)
            except Exception, e:
                raise forms.ValidationError(e)
                
        return data
    
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
