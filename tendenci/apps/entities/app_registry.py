from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import LogRegistry
from tendenci.apps.entities.models import Entity

class EntityRegistry(LogRegistry):
    # entities - TURQUOISE base - complement is ?????
    event_logs = {
        'entity':{
            'base':('290000', '00FFCC'),
            'add':('291000', '00FFCC'),
            'edit':('292000', '33FFCC'),
            'delete':('293000', '33FF66'),
            'search':('294000', '66FFCC'),
            'view':('295000', '99FFCC'),
        },
    }

site.register(Entity, EntityRegistry)
