from django import forms

from tendenci.apps.entities.models import Entity
from tendenci.core.perms.forms import TendenciBaseForm


class EntityForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'),))
    
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

        fieldsets = [('Entity Information', {
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
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['admin_notes',
                                 'status_detail'], 
                      'classes': ['admin-only'],
                    })]
              
    def __init__(self, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)

        if not self.user.profile.is_superuser:
            if 'admin_notes' in self.fields: self.fields.pop('admin_notes')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
            
