import inspect

from django.contrib import admin
from django.utils.encoding import iri_to_uri
from django.core.urlresolvers import reverse
from django.conf import settings

from tendenci.core.event_logs.models import EventLog
from tendenci.core.perms.utils import update_perms_and_save


class TendenciBaseModelAdmin(admin.ModelAdmin):
    """
    Base ModelAdmin class to help with event logs
    """

    class Media:
        js = ('%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,)

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

    def owner_link(self, obj):
        link = ''
        if obj.owner_username:
            link = '<a href="%s" title="%s">%s</a>' % (
                reverse('profile', args=[obj.owner_username]),
                obj.owner_username,
                obj.owner_username,
            )
        return link
    owner_link.allow_tags = True
    owner_link.short_description = 'owner'

    def admin_status(self, obj):
        return obj.obj_status
    admin_status.allow_tags = True
    admin_status.short_description = 'status'

    def admin_perms(self, obj):
        return obj.obj_perms
    admin_perms.allow_tags = True
    admin_perms.short_description = 'permission'

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

    def change_view(self, request, object_id, form_url='', extra_context=None):
        result = super(TendenciBaseModelAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)
        if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

    def log_deletion(self, request, object, object_repr):
        application = inspect.getmodule(self).__name__
        super(TendenciBaseModelAdmin, self).log_deletion(request, object, object_repr)
