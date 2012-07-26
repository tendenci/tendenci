from haystack import indexes
from haystack import site

from tendenci.core.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.tenants.models import Tenant, Map

class MapIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name',)

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_order(self, obj):
        return obj.update_dt


class TenantIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name',)

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_order(self, obj):
        return obj.update_dt

site.register(Tenant, TenantIndex)
site.register(Map, MapIndex)
