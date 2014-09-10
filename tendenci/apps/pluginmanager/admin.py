from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.pluginmanager.models import PluginApp
from tendenci.apps.pluginmanager.forms import PluginAppForm


class PluginAppAdmin(admin.ModelAdmin):
    list_display = ['edit_link', 'view_app', 'description', 'is_enabled']
    list_filter = ['is_enabled']
    search_fields = ['title', 'description']
    actions = None
    form = PluginAppForm

    def edit_link(self, obj):
        return "Edit"
    edit_link.short_description = _('edit')

    def view_app(self, obj):
        if obj.is_enabled:
            link = '<strong><a href="/admin/%s/">%s</a></strong>' % (
            obj.package.split('.')[-1], obj.title
            )
            return link
        else:
            return obj.title
    view_app.allow_tags = True
    view_app.short_description = _('view')

    # Hide the add button since addons are auto added to the list
    def has_add_permission(self, request):
        return False

# admin.site.register(PluginApp, PluginAppAdmin)
