from tastypie import fields
from tastypie.validation import CleanedDataFormValidation
from api_tasty.resources import TendenciResource
from memberships.models import Membership

class MembershipResource(TendenciResource):
    class Meta(TendenciResource.Meta):
        queryset = Membership.objects.all()
        resource_name = 'membership'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        
