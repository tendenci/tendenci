from django.contrib import admin
from tendenci.core.event_logs.models import EventLog
from tendenci.core.perms.utils import update_perms_and_save
from tendenci.apps.entities.models import Entity


class EntityAdmin(admin.ModelAdmin):
    list_display = ['id', 'entity_name', 'entity_type', 'entity_parent', 'status', 'status_detail']
    list_editable = ['entity_name', 'entity_type']
    list_filter = ['entity_type', 'status', 'status_detail']
    search_fields = ['entity_name']
    fieldsets = (
        (None, {
            'fields': (
            'entity_name',
            'entity_type',
            'entity_parent',
            'status_detail',
            'status',
        )},),
    )

    def save_model(self, request, object, form, change):
        """
        Update the permissions backend and log the event
        """
        instance = form.save(commit=False)
        instance = update_perms_and_save(request, form, instance)
        log_defaults = {
            'instance': object,
            'action': "edit"
        }
        if not change:
            log_defaults['action'] = "add"

        EventLog.objects.log(**log_defaults)
        return instance


admin.site.register(Entity, EntityAdmin)

