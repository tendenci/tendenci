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

    def edit_link(self, obj):
        return "Edit"
    edit_link.short_description = 'edit'

    def view_app(self, obj):
        link = '<a href="/admin/%s/">%s</a>' % (
        obj.package.split('.')[-1], obj.title
        )
        return link
    view_app.allow_tags = True
    view_app.short_description = 'view'

    # Hide the add button since addons are auto added to the list
    def has_add_permission(self, request):
        return False

admin.site.register(PluginApp, PluginAppAdmin)
