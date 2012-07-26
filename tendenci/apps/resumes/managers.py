from tendenci.core.perms.managers import TendenciBaseManager
from tendenci.core.base.utils import now_localized

class ResumeManager(TendenciBaseManager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query resumes. 
            Returns a SearchQuerySet
        """
        sqs = super(ResumeManager, self).search(query=None, *args, **kwargs)
        if self.user.is_anonymous():
            sqs = sqs.filter(activation_dt__lte=now_localized())
            sqs = sqs.filter(expiration_dt__gte=now_localized())
        return sqs