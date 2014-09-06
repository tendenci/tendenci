from tastypie import fields
from tendenci.apps.profiles.models import Profile
from tendenci.apps.entities.models import Entity
from tendenci.apps.api_tasty.validation import TendenciValidation
from tendenci.apps.api_tasty.resources import TendenciResource
from tendenci.apps.api_tasty.users.resources import UserResource
from tendenci.apps.api_tasty.entities.resources import EntityResource
from tendenci.apps.api_tasty.profiles.forms import ProfileForm

class ProfileResource(TendenciResource):
    """Profile API
    list:
    *example: http://0.0.0.0:8000/api_tasty/v1/profile/?format=json&username=sam&api_key=6f21b5cad4841d7ba76e6d76d5b9332dddf109bf
    create:
    *example: curl -H "Content-Type: application/json" -X POST --data @data.json "http://0.0.0.0:8000/api_tasty/v1/profile/?format=json&username=sam&api_key=6f21b5cad4841d7ba76e6d76d5b9332dddf109bf"
    update:
    curl -H "Content-Type: application/json" -X PUT --data @data.json "http://0.0.0.0:8000/api_tasty/v1/profile/12/?format=json&username=sam&api_key=6f21b5cad4841d7ba76e6d76d5b9332dddf109bf"
    *update options: same sa create's options
    delete:
    *example: curl -H "Content-Type: application/json" -X DELETE "http://0.0.0.0:8000/api_tasty/v1/profile/12/?format=json&username=sam&api_key=6f21b5cad4841d7ba76e6d76d5b9332dddf109bf"
    """

    user = fields.ForeignKey(UserResource, 'user')
    entity = fields.ForeignKey(EntityResource, 'entity', null=True)

    class Meta(TendenciResource.Meta):
        queryset = Profile.objects.all()
        resource_name = 'profile'
        validation = TendenciValidation(form_class=ProfileForm)
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']


