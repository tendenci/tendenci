from tastypie import fields
from tastypie.resources import ModelResource
from tendenci.core.api_tasty.resources import TendenciResource
from tendenci.core.api_tasty.validation import TendenciValidation
from tendenci.core.api_tasty.entities.resources import EntityResource
from tendenci.addons.events.models import Event, Place, Type

class PlaceResource(ModelResource):
    class Meta:
        queryset = Place.objects.all()
        resource_name = 'place'
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]

class TypeResource(ModelResource):
    class Meta:
        queryset = Type.objects.all()
        resource_name = 'type'
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]

class EventResource(TendenciResource):
    entity = fields.ForeignKey(EntityResource, 'entity', null=True)
    type = fields.ForeignKey(TypeResource, 'type', null=True)
    place = fields.ForeignKey(PlaceResource, 'place', null=True)

    class Meta(TendenciResource.Meta):
        queryset = Event.objects.all()
        resource_name = 'event'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
