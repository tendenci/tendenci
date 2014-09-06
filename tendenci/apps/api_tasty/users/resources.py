import random

from django.contrib.auth.models import User

from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.validation import CleanedDataFormValidation
from tastypie import fields

from tendenci.apps.api_tasty.auth import DeveloperApiKeyAuthentication
from tendenci.apps.api_tasty.serializers import SafeSerializer
from tendenci.apps.api_tasty.users.forms import UserForm

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        serializer = SafeSerializer()
        authorization = Authorization()
        authentication = DeveloperApiKeyAuthentication()
        validation = CleanedDataFormValidation(form_class=UserForm)
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']
        excludes = ['username', 'password']

    def dehydrate(self, bundle):
        bundle.data['username'] = bundle.obj.username
        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        bundle = super(UserResource, self).obj_create(bundle, request, **kwargs)
        bundle.obj.set_password(bundle.data.get('password'))
        bundle.obj.save()
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        bundle = super(UserResource, self).obj_update(bundle, request, **kwargs)
        password = bundle.data.get('password')
        if password:
            bundle.obj.set_password(password)
        bundle.obj.save()
        return bundle

