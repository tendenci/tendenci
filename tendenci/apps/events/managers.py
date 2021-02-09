import operator
from haystack.query import SearchQuerySet
from functools import reduce

from django.db.models import Manager
from django.db.models import Q
from django.contrib.auth.models import User

from tendenci.apps.perms.managers import TendenciBaseManager


class EventManager(TendenciBaseManager):
    def search(self, query=None, *args, **kwargs):
        """
        Uses haystack to query events.
        Returns a SearchQuerySet
        """
        sqs = super(EventManager, self).search(query=query, *args, **kwargs)

        start_dt, end_dt = kwargs.get('date_range', (None, None))

        if start_dt and end_dt:
            sqs = sqs.filter(start_dt__lte=start_dt, end_dt__gte=end_dt)
        else:
            # old behavior
            if start_dt:
                # this does not take into account events that are still active
                # this only takes into account events starting after the given date.
                sqs = sqs.filter(start_dt__gte=start_dt)
            elif end_dt:
                # this does not take into account events that are active before the given date.
                # this only takes into account events that will end before the given date.
                sqs = sqs.filter(end_dt__lte=end_dt)

        # sorting must be done outside this function
        # for some reason a 2nd call to order_by fails to sort again
        # if not query:
        # sort based on start_dt by default
        #    sqs = sqs.order_by('start_dt')
        #print sqs #will force the search query to be evaluated
        return sqs

    def search_filter(self, filters=None, *args, **kwargs):
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)
        groups = []
        if user and user.is_authenticated:
            groups = [g.pk for g in user.user_groups.all()]

        # permission filters
        if user:
            if not user.profile.is_superuser:
                if not user.is_anonymous:
                    # (status+status_detail+(anon OR user)) OR (who_can_view__exact)
                    anon_query = Q(allow_anonymous_view=True)
                    user_query = Q(allow_user_view=True)
                    sec1_query = Q(status=True, status_detail='active')
                    user_perm_q = Q(users_can_view__in=[user.pk])
                    group_perm_q = Q(groups_can_view__in=groups)

                    query = reduce(operator.or_, [anon_query, user_query])
                    query = reduce(operator.and_, [sec1_query, query])
                    query = reduce(operator.or_, [query, user_perm_q, group_perm_q])
                else:
                    sqs = sqs.filter(allow_anonymous_view=True)
        else:
            sqs = sqs.filter(allow_anonymous_view=True)

        # custom filters
        for filter in filters:
            sqs = sqs.filter(content='"%s"' % filter)

        return sqs.models(self.model)
    
    def get_queryset(self):
        """
        Exclude events with status_detail 'template'.
        """
        return super(EventManager, self).get_queryset().exclude(status_detail='template')
    
    def get_queryset_templates(self):
        """
        Returns events with status_detail 'template'.
        """
        return super(EventManager, self).get_queryset().filter(status_detail='template')
    
    def get_all(self):
        """
        Gets all events including status_detail 'template'.
        """
        return super(EventManager, self).get_queryset()


class EventTypeManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query events.
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)

        # check to see if there is impersonation
        if hasattr(user, 'impersonated_user'):
            if isinstance(user.impersonated_user, User):
                user = user.impersonated_user

        if query:
            sqs = sqs.auto_query(sqs.query.clean(query))

        return sqs.models(self.model)


class RegistrantManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
        Uses haystack to query events.
        Returns a SearchQuerySet
        """
        #sqs = SearchQuerySet()
        sqs = kwargs.pop('sqs', SearchQuerySet())
        event = kwargs.get('event')

        if event:
            sqs = sqs.filter(event_pk=event.pk)

        # let the parent search know that we have started a SQS
        kwargs.update({'sqs': sqs})

        sqs = super(RegistrantManager, self).search(
            query=query, *args, **kwargs)

        return sqs
