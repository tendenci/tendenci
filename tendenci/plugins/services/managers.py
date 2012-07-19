from perms.managers import TendenciBaseManager
from base.utils import now_localized


class ServiceManager(TendenciBaseManager):
    def search(self, query=None, *args, **kwargs):
        """
        Uses haystack to query resumes.
        Returns a SearchQuerySet
        """
        sqs = super(ServiceManager, self).search(query, *args, **kwargs)
        if self.user.is_anonymous():
            sqs = sqs.filter(activation_dt__lte=now_localized())
            sqs = sqs.filter(expiration_dt__gte=now_localized())
        return sqs
