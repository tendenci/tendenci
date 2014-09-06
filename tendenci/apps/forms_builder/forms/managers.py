from django.contrib.auth.models import User
from tendenci.apps.perms.managers import TendenciBaseManager

from haystack.query import SearchQuerySet


class FormManager(TendenciBaseManager):
    """
    Only show published forms for non-staff users.
    """
    def published(self, for_user=None):
        if for_user is not None and for_user.is_staff:
            return self.all()
        return self.filter(status_detail='published')

    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query forms.
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)

        # check to see if there is impersonation
        if hasattr(user, 'impersonated_user'):
            if isinstance(user.impersonated_user, User):
                user = user.impersonated_user

        is_an_admin = user.profile.is_superuser

        if query:
            sqs = sqs.auto_query(sqs.query.clean(query))
            if user:
                if not is_an_admin:
                    return []
        else:
            sqs = sqs.all()
            if user:
                if not is_an_admin:
                    return []

        return sqs.models(self.model).order_by('-create_dt')
