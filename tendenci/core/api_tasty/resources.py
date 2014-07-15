from django.contrib.auth.models import User

from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie import fields

from tendenci.core.api_tasty.serializers import SafeSerializer
from tendenci.core.api_tasty.auth import DeveloperApiKeyAuthentication
from tendenci.core.api_tasty.users.resources import UserResource

class TendenciResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner')
    creator = fields.ForeignKey(UserResource, 'creator')

    class Meta:
        serializer = SafeSerializer()
        authorization = Authorization()
        authentication = DeveloperApiKeyAuthentication()

