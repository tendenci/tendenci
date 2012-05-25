from api_tasty.resources import TendenciResource
from discounts.models import Discount

class DiscountResource(TendenciResource):
    class Meta(TendenciResource.Meta):
        queryset = Discount.objects.all()
        resource_name = 'discount'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
