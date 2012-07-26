from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie import fields

from tendenci.core.api_tasty.auth import DeveloperApiKeyAuthentication
from tendenci.core.api_tasty.serializers import SafeSerializer
from tendenci.core.payments.models import PaymentMethod

class PaymentMethodResource(ModelResource):
    class Meta:
        queryset = PaymentMethod.objects.all()
        resource_name = 'payment_method'
        serializer = SafeSerializer()
        authorization = Authorization()
        authentication = DeveloperApiKeyAuthentication()
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
