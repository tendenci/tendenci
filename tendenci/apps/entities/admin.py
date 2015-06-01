from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.utils import update_perms_and_save
from tendenci.apps.entities.models import Entity


ENTITY_TYPES = (
    ('', _('SELECT ONE')),
    ('Committee', _('Committee')),
    ('Reporting', _('Reporting')),
    ('Study Group', _('Study Group')),
    ('Technical Interest Group', _('Technical Interest Group')),
    ('Other', _('Other')),
)


class EntityAdminForm(forms.ModelForm):
    entity_type = forms.ChoiceField(choices=ENTITY_TYPES)

    class Meta:
        model = Entity
        # django 1.8 requires either 'fields' or 'exclude' for ModelForm
        fields = (
            'entity_name',
            'entity_type',
            'entity_parent',
            'status_detail',)


class EntityAdmin(admin.ModelAdmin):
    form = EntityAdminForm
    list_display = ['id', 'entity_name', 'entity_type', 'entity_parent', 'status_detail']
    list_editable = ['entity_name', 'entity_type']
    list_filter = ['entity_parent', 'status_detail']
    search_fields = ['entity_name']
    fieldsets = (
        (None, {
            'fields': (
            'entity_name',
            'entity_type',
            'entity_parent',
            'status_detail',)},),
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

    def get_changelist_form(self, request, **kwargs):
        kwargs.setdefault('form', EntityAdminForm)
        return super(EntityAdmin, self).get_changelist_form(request, **kwargs)

admin.site.register(Entity, EntityAdmin)
