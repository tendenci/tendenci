from django import forms

from entities.models import Entity
from perms.forms import TendenciBaseForm
from perms.utils import is_admin

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
        'status',
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
                                 'status',
                                 'status_detail'], 
                      'classes': ['admin-only'],
                    })]
              
    def __init__(self, user=None, *args, **kwargs):
        self.user = user 
        super(EntityForm, self).__init__(user, *args, **kwargs)

        if not is_admin(user):
            if 'admin_notes' in self.fields: self.fields.pop('admin_notes')
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
            