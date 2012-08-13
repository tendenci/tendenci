from django.contrib.auth.models import User

class ProfileMiddleware(object):
    """
        Appends a profile instance to anonymous users.
        Creates a profile for logged in users without one.
    """
    def process_request(self, request):
        from tendenci.apps.profiles.models import Profile
        if request.user.is_anonymous():
            request.user.profile = Profile(status=False, status_detail="inactive", user=User(is_staff=False, is_superuser=False, is_active=False))
        else:
            try:
                profile = request.user.get_profile()
            except Profile.DoesNotExist:
                profile = Profile.objects.create_profile(user=request.user)