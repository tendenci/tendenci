from django.contrib import admin
from tendenci.apps.pluginmanager.models import PluginApp
from tendenci.apps.pluginmanager.forms import PluginAppForm

class PluginAppAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'package', 'is_installed', 'is_enabled']
    list_filter = ['is_installed', 'is_enabled']
    form = PluginAppForm

admin.site.register(PluginApp, PluginAppAdmin)
