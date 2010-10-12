from django.contrib import admin
from models import PluginApp

class PluginAppAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'package', 'is_installed', 'is_enabled']
    list_filter = ['is_installed', 'is_enabled']


admin.site.register(PluginApp, PluginAppAdmin)
