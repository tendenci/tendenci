from django.contrib import admin
from plugin_builder.models import Plugin, PluginField
from plugin_builder.forms import PluginForm

class PluginFieldInline(admin.TabularInline):
    model = PluginField

class PluginAdmin(admin.ModelAdmin):
    form = PluginForm
    inlines = [
        PluginFieldInline,
    ]

admin.site.register(Plugin, PluginAdmin)
