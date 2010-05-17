from base.auth import BasePermission
from releases.models import Release
from authority import register

class ReleasePermission(BasePermission):
    """
        Permissions for releases
    """
    label = 'release_permission'
    
register(Release, ReleasePermission)