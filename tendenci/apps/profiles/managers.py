from tendenci.core.perms.managers import TendenciBaseManager


class ProfileManager(TendenciBaseManager):

    def create_profile(self, user):
        return self.create(user=user,
                           creator_id=user.id,
                           creator_username=user.username,
                           owner_id=user.id,
                           owner_username=user.username)

    def search(self, query=None, *args, **kwargs):
        """
        Uses haystack to user.
        Returns a SearchQuerySet.
        Filter out users if they have hide_in_search set to True.
        """
        sqs = super(ProfileManager, self).search(query=query, *args, **kwargs)
        if not kwargs.get('user').profile.is_superuser:
            sqs = sqs.filter(hide_in_search=False)
        return sqs

class ProfileActiveManager(TendenciBaseManager):
    def get_query_set(self):
        return super(ProfileActiveManager, self).get_query_set().filter(status=True, status_detail='active', user__is_active=True)
