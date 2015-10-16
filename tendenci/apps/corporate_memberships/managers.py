from django.db.models import Manager

from tendenci.apps.perms.managers import TendenciBaseManager


class CorpMembershipManager(TendenciBaseManager):
    def search(self, query=None, *args, **kwargs):
        """
        haystack to query corporate memberships.
        Returns a SearchQuerySet
        """
        return super(CorpMembershipManager, self).search(query=query, *args, **kwargs)

class CorpMembershipAppManager(Manager):
    def current_app(self, **kwargs):
        """
        Returns the app being used currently.
        """
        [current_app] = self.filter(
                           status=True,
                           status_detail__in=['active', 'published']
                           ).order_by('id')[:1] or [None]

        return current_app
