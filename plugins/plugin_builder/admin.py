from django.contrib import admin
from plugin_builder.models import Plugin, PluginField
from plugin_builder.forms import PluginForm, PluginFieldForm
from plugin_builder.utils import build_plugin

class PluginFieldInline(admin.TabularInline):
    model = PluginField
    form = PluginFieldForm

class PluginAdmin(admin.ModelAdmin):
    form = PluginForm
    inlines = [
        PluginFieldInline,
    ]
    actions = ['build_plugins']
    
    def build_plugins(self, request, queryset):
        message_bit = ""
        for plugin in queryset:
            build_plugin(plugin)
            message_bit = message_bit + ", %s" % plugin.plural_lower
        self.message_user(request, "Successfully built the following plugins:%s" % message_bit[1:])
    build_plugins.short_description = "Build/Rebuild selected plugins."

admin.site.register(Plugin, PluginAdmin)
