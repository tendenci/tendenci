import operator

from django.db.models import Manager
from django.db.models import Q

from haystack.query import SearchQuerySet
from perms.utils import is_admin

class JobManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query jobs. 
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)
        is_an_admin = is_admin(user)
            
        if query:
            sqs = sqs.auto_query(sqs.query.clean(query)) 
            if user:
                if not is_an_admin:
                    if not user.is_anonymous():
                    # if b/w admin and anon

                        # (status+status_detail+(anon OR user)) OR (who_can_view__exact)
                        anon_query = Q(**{'allow_anonymous_view':True,})
                        user_query = Q(**{'allow_user_view':True,})
                        sec1_query = Q(**{
                            'status':1,
                            'status_detail':'active',
                        })
                        sec2_query = Q(**{
                            'who_can_view__exact':user.username
                        })
                        query = reduce(operator.or_, [anon_query, user_query])
                        query = reduce(operator.and_, [sec1_query, query])
                        query = reduce(operator.or_, [query, sec2_query])

                        sqs = sqs.filter(query)
                    else:
                    # if anonymous
                        sqs = sqs.filter(status=1).filter(status_detail='active')
                        sqs = sqs.filter(allow_anonymous_view=True)
            else:
                # if anonymous
                sqs = sqs.filter(status=1).filter(status_detail='active')
                sqs = sqs.filter(allow_anonymous_view=True)
        else:
            if user:
                if is_an_admin:
                    sqs = sqs.all()
                else:
                    if not user.is_anonymous():
                        # (status+status_detail+anon OR who_can_view__exact)
                        sec1_query = Q(**{
                            'status':1,
                            'status_detail':'active',
                            'allow_anonymous_view':True,
                        })
                        sec2_query = Q(**{
                            'who_can_view__exact':user.username
                        })
                        query = reduce(operator.or_, [sec1_query, sec2_query])
                        sqs = sqs.filter(query)
                    else:
                        # if anonymous
                        sqs = sqs.filter(status=1).filter(status_detail='active')
                        sqs = sqs.filter(allow_anonymous_view=True)               
            else:
                # if anonymous
                sqs = sqs.filter(status=1).filter(status_detail='active')
                sqs = sqs.filter(allow_anonymous_view=True)

            sqs = sqs.order_by('-create_dt')
    
        return sqs.models(self.model)