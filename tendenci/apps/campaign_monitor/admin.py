from django.contrib import admin
from tendenci.apps.campaign_monitor.forms import CampaignForm, TemplateForm


class TemplateAdmin(admin.ModelAdmin):
    form = TemplateForm


class CampaignAdmin(admin.ModelAdmin):
    form = CampaignForm

# admin.site.register(Template, TemplateAdmin)
# admin.site.register(Campaign, CampaignAdmin)
