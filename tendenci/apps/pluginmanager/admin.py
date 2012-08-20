from django.contrib import admin

from tendenci.apps.pluginmanager.models import PluginApp
from tendenci.apps.pluginmanager.forms import PluginAppForm


class PluginAppAdmin(admin.ModelAdmin):
    list_display = ['view_app', 'description', 'is_enabled']
    list_filter = ['is_enabled']
    list_editable = ['is_enabled']
    search_fields = ['title', 'description']
    actions = None
    form = PluginAppForm

    def view_app(self, obj):
        link = '<a href="/admin/%s/">%s</a>' % (
        obj.package.split('.')[-1], obj.title
        )
        return link
    view_app.allow_tags = True
    view_app.short_description = 'view'

admin.site.register(PluginApp, PluginAppAdmin)
