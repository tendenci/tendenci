from tastypie import fields
from tastypie.validation import CleanedDataFormValidation
from profiles.models import Profile
from entities.models import Entity
from api_tasty.resources import TendenciResource
from api_tasty.users.resources import UserResource
from api_tasty.entities.resources import EntityResource
from api_tasty.profiles.forms import ProfileForm

class ProfileResource(TendenciResource):
    user = fields.ForeignKey(UserResource, 'user')
    entity = fields.ForeignKey(EntityResource, 'entity', null=True)
    
    class Meta(TendenciResource.Meta):
        queryset = Profile.objects.all()
        resource_name = 'profile'
        validation = CleanedDataFormValidation(form_class=ProfileForm)
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        fields = [
            'salutation',
            'user',
            'phone',
            'phone2',
            'fax',
            'work_phone',
            'home_phone',
            'mobile_phone',
            'email',
            'email2',
            'company',
            'position_title',
            'position_assignment',
            'display_name',
            'hide_in_search',
            'hide_phone',
            'hide_email',
            'hide_address',
            'initials',
            'sex',
            'mailing_name',
            'address',
            'address2',
            'city',
            'state',
            'zipcode',
            'county',
            'country',
            'url',
            'dob',
            'ssn',
            'spouse',
            'time_zone',
            'department',
            'education',
            'student',
            'direct_mail',
            'notes',
            'allow_anonymous_view',
            'admin_notes',
            'entity',
            'status',
            'status_detail',
        ]
        
