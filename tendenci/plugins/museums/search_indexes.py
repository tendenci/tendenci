from haystack import indexes
from haystack import site

from perms.indexes import TendenciBaseSearchIndex
from museums.models import Museum

class MuseumIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    phone = indexes.CharField(model_attr='phone')
    address = indexes.CharField(model_attr='address')
    city = indexes.CharField(model_attr='city')
    state = indexes.CharField(model_attr='state')
    zip = indexes.CharField(model_attr='zip')
    website = indexes.CharField(model_attr='website')
    
    hours = indexes.CharField(model_attr='hours')
    free_times = indexes.CharField(model_attr='free_times')
    free_parking = indexes.BooleanField(model_attr='free_parking', null=True)
    street_parking = indexes.BooleanField(model_attr='street_parking', null=True)
    paid_parking = indexes.BooleanField(model_attr='paid_parking')
    restaurant = indexes.BooleanField(model_attr='restaurant')
    snacks = indexes.BooleanField(model_attr='snacks')
    events = indexes.CharField(model_attr='events')
    ordering = indexes.IntegerField(model_attr='ordering')
    
    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_syndicate_order(self, obj):
        return obj.update_dt

site.register(Museum, MuseumIndex)
