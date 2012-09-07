from django.contrib import admin
from tendenci.core.registry import admin_registry
from tendenci.addons.campaign_monitor.models import Campaign, Template
from tendenci.addons.campaign_monitor.forms import CampaignForm, TemplateForm

class TemplateAdmin(admin.ModelAdmin):
    form = TemplateForm
    
class CampaignAdmin(admin.ModelAdmin):
    form = CampaignForm

#admin_registry.site.register(Template, TemplateAdmin)
#admin_registry.site.register(Campaign, CampaignAdmin)
