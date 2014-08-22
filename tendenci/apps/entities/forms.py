from django import forms
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.entities.models import Entity
from tendenci.core.perms.forms import TendenciBaseForm


class EntityForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')),))

    class Meta:
        model = Entity
        fields = (
        'entity_name',
        'contact_name',
        'phone',
        'fax',
        'email',
        'website',
        'summary',
        'notes',
        'admin_notes',
        'status_detail',
        )

        fieldsets = [(_('Entity Information'), {
                      'fields': ['entity_name',
                                 'contact_name',
                                 'phone',
                                 'fax',
                                 'email',
                                 'source',
                                 'website',
                                 'summary',
                                 ],
                      'legend': ''
                      }),
                      (_('Permissions'), {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     (_('Administrator Only'), {
                      'fields': ['admin_notes',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)

        if not self.user.profile.is_superuser:
            if 'admin_notes' in self.fields: self.fields.pop('admin_notes')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
