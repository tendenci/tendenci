class ImpersonationMiddleware(object):
    """
        Allows you to impersonate another user for
        a single request only.
    """
    def process_request(self, request):
        if 'impersonate' in request.GET:
            # lets not allow the world to do this in the beginning
            if request.user.is_authenticated and request.user.is_superuser:
                from django.contrib.auth.models import User
                username = request.GET['impersonate']
                try:
                    user = User.objects.get(username=username)
                    request.user = user
                except:
                    user = None
                
            