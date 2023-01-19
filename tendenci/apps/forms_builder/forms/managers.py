from django.contrib.auth.models import User
from tendenci.apps.perms.managers import TendenciBaseManager
from tendenci.apps.perms.utils import has_perm

from haystack.query import SearchQuerySet


class FormManager(TendenciBaseManager):
    """
    Only show published forms for non-staff users.
    """
    def published(self, for_user=None):
        if for_user is not None and (for_user.is_staff or has_perm(for_user,'forms.change_form')):
            return self.all()
        return self.filter(status_detail='published')

    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query forms.
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)

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
