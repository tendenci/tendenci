from django.db.models import Manager
from django.db.models import Q
from haystack.query import SearchQuerySet


class CorporateMembershipManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
        haystack to query corporate memberships.
        Returns a SearchQuerySet
        """
        from corporate_memberships.models import CorporateMembership
        from perms.utils import is_admin

        user = kwargs.get('user', None)
        if user.is_anonymous():
            return None

        is_an_admin = is_admin(user)

        sqs = SearchQuerySet().models(CorporateMembership)

        if query:
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()
        if not is_an_admin:
            # reps__contain
            sqs = sqs.filter(Q(content=sqs.query.clean('rep:%s' % user.username)) |
                             Q(creator=user) |
                             Q(owner=user)).filter(status_detail='active')

        return sqs
