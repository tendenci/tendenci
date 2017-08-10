import operator
from haystack.query import SearchQuerySet

from django.db.models import Manager
from django.db.models import Q
from django.contrib.auth.models import User, AnonymousUser

from tendenci.apps.perms.managers import TendenciBaseManager
from tendenci.apps.site_settings.utils import get_global_setting
from functools import reduce


class GroupManager(TendenciBaseManager):
    def first(self, **fiters):
        groups = self.filter(status=True,
                             status_detail='active'
                            ).order_by('id')
        if fiters:
            groups = groups.filter(**fiters)
        [group] = groups[:1] or [None]

        return group

    def get_or_create_default(self, user=AnonymousUser()):
        from tendenci.apps.entities.models import Entity
        from tendenci.apps.site_settings.utils import get_global_setting
        group = self.first()
        if not group:
            entity = Entity.objects.first()
            if not entity:
                entity = Entity.objects.get_or_create_default(user)
            params = {'name': get_global_setting('sitedisplayname') or 'Tendenci',
                  'dashboard_url': '',
                  'entity': entity,
                  'type': 'distribution',
                  'email_recipient': get_global_setting('sitecontactemail'),
                  'allow_anonymous_view': True,
                  'status': True,
                  'status_detail': 'active'
                  }
            if not user.is_anonymous():
                params.update({'creator': user,
                               'creator_username': user.username,
                               'owner': user,
                               'owner_username': user.username
                               })
            else:
                params.update({'creator_username': '',
                               'owner_username': ''
                               })
            group = self.create(**params)

        return group

    def get_initial_group_id(self):
        """
        Returns the id of the default group.
        Can be used to set group initial for forms.
        """
        group_id = get_global_setting('default_group')
        if not group_id:
            group = self.get_or_create_default()
            group_id = group.id

        return group_id


class OldGroupManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query groups.
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)

        # check to see if there is impersonation
        if hasattr(user,'impersonated_user'):
            if isinstance(user.impersonated_user, User):
                user = user.impersonated_user

        is_a_superuser = user.profile.is_superuser

        if query:
            sqs = sqs.auto_query(sqs.query.clean(query))
            if user:
                if not is_a_superuser:
                    if not user.is_anonymous():
                    # if b/w superuser and anon

                        # (status+status_detail+(anon OR user)) OR (who_can_view__exact)
                        anon_query = Q(**{'allow_anonymous_view':True,})
                        user_query = Q(**{'allow_user_view':True,})
                        sec1_query = Q(**{
                            'show_as_option':1,
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
                    else: # anonymous
                        query = Q(**{
                            'allow_anonymous_view': True,
                            'show_as_option':1,
                            'status':1,
                            'status_detail':'active',
                        })
                        sqs = sqs.filter(query)
            else: # anonymous
                query = Q(**{
                    'allow_anonymous_view': True,
                    'show_as_option':1,
                    'status':1,
                    'status_detail':'active',
                })
                sqs = sqs.filter(query)
        else:
            if user:
                if is_a_superuser:
                    # this is no-op. the .all().exclude(type='membership').models(Group) wouldn't work
                    #sqs = sqs.all()
                    sqs = sqs.filter(status=True)
                else:
                    if not user.is_anonymous():
                        # (status+status_detail+anon OR who_can_view__exact)
                        anon_query = Q(**{'allow_anonymous_view':True,})
                        user_query = Q(**{'allow_user_view':True,})
                        sec1_query = Q(**{
                            'show_as_option':1,
                            'status':1,
                            'status_detail':'active',
                        })
                        sec2_query = Q(**{
                            'who_can_view__exact': user.username
                        })
                        query = reduce(operator.or_, [anon_query, user_query])
                        query = reduce(operator.and_, [sec1_query, query])
                        query = reduce(operator.or_, [query, sec2_query])
                        sqs = sqs.filter(query)
                    else: # anonymous
                        query = Q(**{
                            'allow_anonymous_view': True,
                            'show_as_option':1,
                            'status':1,
                            'status_detail':'active',
                        })
                        sqs = sqs.filter(query)
            else: # anonymous
                query = Q(**{
                    'allow_anonymous_view': True,
                    'show_as_option':1,
                    'status':1,
                    'status_detail':'active',
                })
                sqs = sqs.filter(query)

        sqs = sqs.order_by('-create_dt')

        return sqs.models(self.model)

