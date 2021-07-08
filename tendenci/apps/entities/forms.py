from django import forms
from django.utils.translation import gettext_lazy as _

from tendenci.libs.form_utils.forms import BetterModelForm
from tendenci.apps.entities.models import Entity
from tendenci.apps.base.forms import FormControlWidgetMixin


class EntityForm(FormControlWidgetMixin, BetterModelForm):
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
        'show_for_donation',
        'allow_anonymous_view',
        'allow_user_view',
        'allow_member_view',
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
                                 'show_for_donation',
                                 ],
                      'legend': ''
                      }),
                      (_('Permissions'), {
                      'fields': ['allow_anonymous_view',
                                 'allow_user_view',
                                 'allow_member_view',
                                 ],
                      }),
                     (_('Administrator Only'), {
                      'fields': ['admin_notes',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EntityForm, self).__init__(*args, **kwargs)

        if not self.user.profile.is_superuser:
            if 'admin_notes' in self.fields: self.fields.pop('admin_notes')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
