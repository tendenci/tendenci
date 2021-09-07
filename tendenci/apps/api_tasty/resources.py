from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie import fields

from tendenci.apps.api_tasty.serializers import SafeSerializer
from tendenci.apps.api_tasty.auth import DeveloperApiKeyAuthentication
from tendenci.apps.api_tasty.users.resources import UserResource

class TendenciResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', null=True, full=True)
    creator = fields.ForeignKey(UserResource, 'creator', null=True, full=True)

    class Meta:
        #abstract = True
        object_class = None  # Replaced by abstract=True in tastypie 0.14.1
        serializer = SafeSerializer()
        authorization = Authorization()
        authentication = DeveloperApiKeyAuthentication()
