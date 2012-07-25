import inspect

from django.contrib import admin
from django.utils.encoding import iri_to_uri
from django.conf import settings

from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.utils import update_perms_and_save


class TendenciBaseModelAdmin(admin.ModelAdmin):
    """
    Base ModelAdmin class to help with event logs
    """

    def __init__(self, *args, **kwargs):
        super(TendenciBaseModelAdmin, self).__init__(*args, **kwargs)

        # Update the list_display to add view_on_site and edit_link if they
        # are not already added. - JMO 2012-05-15
        self.list_display = list(self.list_display)
        if 'action_checkbox' in self.list_display:
            index = self.list_display.index('action_checkbox')
            self.list_display.pop(index)

        if hasattr(self.model, "get_absolute_url"):
            if 'view_on_site' not in self.list_display:
                self.list_display.insert(0, 'view_on_site')

        if 'edit_link' not in self.list_display:
            self.list_display.insert(0, 'edit_link')
        if 'action_checkbox' not in self.list_display:
            self.list_display.insert(0, 'action_checkbox')

        self.list_display_links = ('edit_link', )

    def edit_link(self, obj):
        return "Edit"
    edit_link.short_description = 'edit'

    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            obj.get_absolute_url(),
            obj,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'

    def save_model(self, request, object, form, change):
        """
        Update the permissions backend and log the event
        """
        instance = form.save(commit=False)
        instance = update_perms_and_save(request, form, instance, log=False)
        log_defaults = {
            'instance': object,
            'action': "edit"
        }
        if not change:
            log_defaults['action'] = "add"

        # Handle a special case for bulk reordering via the list view.
        if form.changed_data != ['ordering']:
            EventLog.objects.log(**log_defaults)
        return instance

    def change_view(self, request, object_id, extra_context=None):
        result = super(TendenciBaseModelAdmin, self).change_view(request, object_id, extra_context)
        if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

    def log_deletion(self, request, object, object_repr):
        application = inspect.getmodule(self).__name__
        super(TendenciBaseModelAdmin, self).log_deletion(request, object, object_repr)
