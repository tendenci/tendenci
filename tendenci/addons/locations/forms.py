from tendenci.addons.locations.models import Location
from tendenci.core.perms.forms import TendenciBaseForm
from django import forms

class LocationForm(TendenciBaseForm):

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

    class Meta:
        model = Location
        fields = (
        'location_name',
        'description',
        'contact',
        'address',
        'address2',
        'city',
        'state',
        'zipcode',
        'country',
        'phone',
        'fax',
        'email',
        'website',
        'latitude',
        'longitude',
        'hq',
        'allow_anonymous_view',
        'user_perms',
        'member_perms',
        'group_perms',
        'status',
        'status_detail',
        )

        fieldsets = [('Location Information', {
                      'fields': ['location_name',
                                 'description',
                                 'latitude',
                                 'longitude',
                                 'hq',
                                 ],
                      'legend': ''
                      }),
                      ('Contact', {
                      'fields': ['contact',
                                 'address',
                                 'address2',
                                 'city',
                                 'state',
                                 'zip_code',
                                 'country',
                                 'phone',
                                 'fax',
                                 'email',
                                 'website'
                                 ],
                        'classes': ['contact'],
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['status',
                                 'status_detail'], 
                      'classes': ['admin-only'],
                    })]   
           
    def __init__(self, *args, **kwargs): 
        super(LocationForm, self).__init__(*args, **kwargs)

        if not self.user.profile.is_superuser:
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
