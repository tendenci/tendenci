from tastypie import fields
from profiles.models import Profile
from entities.models import Entity
from api_tasty.validation import TendenciValidation
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
        validation = TendenciValidation(form_class=ProfileForm)
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        
        
