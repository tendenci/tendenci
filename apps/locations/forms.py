from locations.models import Location
from perms.forms import TendenciBaseForm
from django import forms

class LocationForm(TendenciBaseForm):
    STATUS_CHOICES = (('active','Active'),('inactive','Inactive'), ('pending','Pending'),)
    status_detail = forms.ChoiceField(choices=STATUS_CHOICES)

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
        
        
        
        