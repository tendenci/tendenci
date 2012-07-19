from django.contrib import admin
from campaign_monitor.models import Campaign, Template
from campaign_monitor.forms import CampaignForm, TemplateForm

class TemplateAdmin(admin.ModelAdmin):
    form = TemplateForm
    
class CampaignAdmin(admin.ModelAdmin):
    form = CampaignForm

#admin.site.register(Template, TemplateAdmin)
#admin.site.register(Campaign, CampaignAdmin)
