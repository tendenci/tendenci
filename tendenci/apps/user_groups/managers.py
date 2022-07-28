import operator
from haystack.query import SearchQuerySet
from functools import reduce

from django.db.models import Manager
from django.db.models import Q
from django.contrib.auth.models import User, AnonymousUser
from django.template.defaultfilters import slugify

from tendenci.apps.perms.managers import TendenciBaseManager
from tendenci.apps.site_settings.utils import get_global_setting
from tendenci.apps.entities.models import Entity


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
            if not user.is_anonymous:
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

    def create_group(self, name, **kwargs):
        name = name[:200]
        slug = slugify(name)
        # ensure uniqueness of name and slug
        if self.filter(slug=slug).exists():
            tmp_groups = self.filter(slug__istartswith=slug)
            if tmp_groups:
                t_list = [g.slug[len(slug):] for g in tmp_groups]
                num = 1
                while str(num) in t_list:
                    num += 1
                slug = f'{slug}{str(num)}'
                # group name is also a unique field
                name = f'{name}{str(num)}'
        return self.create(name=name,
            slug=slug,
            label=name,
            type=kwargs.get('type', 'distribution'),
            email_recipient=kwargs.get('email_recipient', ''),
            show_as_option=kwargs.get('show_as_option', False),
            allow_self_add=kwargs.get('allow_self_add', False),
            allow_self_remove=kwargs.get('allow_self_remove', False),
            show_for_memberships=kwargs.get('show_for_memberships', False),
            description=kwargs.get('description', ''),
            notes=kwargs.get('notes', ''),
            allow_anonymous_view=kwargs.get('allow_anonymous_view', False),
            allow_user_view=kwargs.get('allow_user_view', False),
            allow_member_view=kwargs.get('allow_member_view', False),
            creator=kwargs.get('creator', None),
            creator_username=kwargs.get('creator_username', ''),
            owner=kwargs.get('owner', None),
            owner_username=kwargs.get('owner_username', ''),
            entity=kwargs.get('entity', Entity.objects.first()),
        )      


class OldGroupManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query groups.
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)

        is_a_superuser = user.profile.is_superuser

        if query:
            sqs = sqs.auto_query(sqs.query.clean(query))
            if user:
                if not is_a_superuser:
                    if not user.is_anonymous:
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
                    if not user.is_anonymous:
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
