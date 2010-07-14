from locations.models import Location
from perms.utils import is_admin
from perms.forms import TendenciBaseForm
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
        'entity',
        'status',
        'status_detail',
        )
   
    def __init__(self, user=None, *args, **kwargs): 
        self.user = user
        super(LocationForm, self).__init__(user, *args, **kwargs)

        if not is_admin(user):
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
        
        
        