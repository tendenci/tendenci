from django import forms

from locations.models import Location
from perms.forms import AuditingBaseForm

class LocationForm(AuditingBaseForm):
#    city = forms.CharField(required=False, max_length=50)
#    state = forms.CharField(required=False, max_length=50)
#    state = forms.CharField(required=False, max_length=100)
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
        'entityid',
        'entityownerid',
        'status',
        'status_detail',
        )
   
    def __init__(self, user=None, *args, **kwargs): 
        self.user = user
        super(LocationForm, self).__init__(user, *args, **kwargs)
        
        
        
        