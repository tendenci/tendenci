from base.auth import BasePermission
from entities.models import Entity
from authority import register

class EntityPermission(BasePermission):
    """
        Permissions for entities
    """
    label = 'entity_permission'
    
register(Entity, EntityPermission)