from tastypie import fields
from entities.models import Entity
from api_tasty.resources import TendenciResource

class EntityResource(TendenciResource):
    class Meta(TendenciResource.Meta):
        queryset = Entity.objects.all()
        resource_name = 'entity'
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
