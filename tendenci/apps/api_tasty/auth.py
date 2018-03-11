from tastypie.authentication import ApiKeyAuthentication

class DeveloperApiKeyAuthentication(ApiKeyAuthentication):
    """
    Extends the build in ApiKeyAuthentication and adds in checking
    for a user's superuser status.
    """

    def get_key(self, user, api_key):
        """
        Attempts to find the API key for the user. Uses ``ApiKey`` by default
        In addition this checks if the user is a superuser.
        If the user is not even if he has a key he will still be unauthorized.
        """
        from tastypie.models import ApiKey

        if not user.profile.is_superuser:
            return self._unauthorized()

        try:
            ApiKey.objects.get(user=user, key=api_key)
        except ApiKey.DoesNotExist:
            return self._unauthorized()

        return True
