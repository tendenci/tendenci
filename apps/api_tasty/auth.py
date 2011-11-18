from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization

from perms.utils import is_developer

class DeveloperApiKeyAuthentication(ApiKeyAuthentication):
    """
    Extends the build in ApiKeyAuthentication and adds in checking
    for a user's developer status.
    """
    
    def get_key(self, user, api_key):
        """
        Attempts to find the API key for the user. Uses ``ApiKey`` by default
        In addition this checks if the user is a developer.
        If the user is not even if he has a key he will still be unauthorized.
        """
        from tastypie.models import ApiKey
        
        if not is_developer(user):
            return self._unauthorized()
        
        try:
            key = ApiKey.objects.get(user=user, key=api_key)
        except ApiKey.DoesNotExist:
            return self._unauthorized()
        
        return True
        
