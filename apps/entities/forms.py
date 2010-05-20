from django import forms
from entities.models import Entity

class EntityForm(forms.ModelForm):
    class Meta:
        model = Entity
        fields = (
        'entity_name',
        'contact_name',
        'phone',
        'fax',
        'email',
        'website',
        'mission',
        'summary',
        'notes',
        'admin_notes',
        )
      
    def __init__(self, user=None, *args, **kwargs):
        self.user = user 
        super(EntityForm, self).__init__(*args, **kwargs)

class EntityEditForm(forms.ModelForm):
    class Meta:
        model = Entity
        fields = (
        'entity_name',
        'contact_name',
        'phone',
        'fax',
        'email',
        'website',
        'mission',
        'summary',
        'notes',
        'admin_notes',
        )
      
    def __init__(self, user=None, *args, **kwargs):
        self.user = user 
        super(EntityEditForm, self).__init__(*args, **kwargs)