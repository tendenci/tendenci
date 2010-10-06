import operator

from django.db.models import Manager
from django.db.models import Q
from django.contrib.auth.models import User

from haystack.query import SearchQuerySet

class ProfileManager(Manager):
    def create_profile(self, user):
        return self.create(user=user, 
                           creator_id=user.id, 
                           creator_username=user.username,
                           owner_id=user.id, 
                           owner_username=user.username, 
                           email=user.email)
        
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to user. 
            Returns a SearchQuerySet
        """
        from perms.utils import is_admin
        from site_settings.utils import get_setting
        
        # set up user and search query set
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)
        is_an_admin = is_admin(user)
        
        # site settings that modify search
        allow_user_search = get_setting('module', 'users', 'allowusersearch')
        allow_anonymous_search = get_setting('module', 'users', 'allowanonymoususersearchuser')

        # check to see if there is impersonation
        if hasattr(user,'impersonated_user'):
            if isinstance(user.impersonated_user, User):
                user = user.impersonated_user

        if query:
            sqs = sqs.auto_query(sqs.query.clean(query)) 
            if user:
                if not is_an_admin:
                    if not user.is_anonymous():
                        if allow_anonymous_search:
                            sub_query1 = Q(**{
                                'hide_in_search': False,
                                'status':1,
                                'status_detail':'active',
                            })        
                            sub_query2 = Q(**{
                                'user_object_exact': user,
                            })                           
                            query = reduce(operator.or_, [sub_query1,sub_query2])
                        else:
                            if not allow_user_search:
                                query = Q(**{
                                    'user_object_exact': user,
                                    'status':1,
                                    'status_detail':'active',
                                })
                            else:
                                sub_query1 = Q(**{
                                    'hide_in_search': False,
                                    'status':1,
                                    'status_detail':'active',
                                })        
                                sub_query2 = Q(**{
                                    'user_object_exact': user,
                                })                           
                                query = reduce(operator.or_, [sub_query1,sub_query2])                  

                        sqs = sqs.filter(query)
                    else: # anonymous
                        if not allow_user_search or not allow_anonymous_search:
                            return sqs.none()
                        query = Q(**{
                            'hide_in_search': False,
                            'status':1,
                            'status_detail':'active',
                        })  
                        sqs = sqs.filter(query)

            else: # anonymous
                if not allow_user_search or not allow_anonymous_search:
                    return sqs.none()
                query = Q(**{
                    'hide_in_search': False,
                    'status':1,
                    'status_detail':'active',
                })  
                sqs = sqs.filter(query)
        else:
            if user:
                if is_an_admin:
                    sqs = sqs.all()
                else:
                    if not user.is_anonymous():
                        if allow_anonymous_search:
                            sub_query1 = Q(**{
                                'hide_in_search': False,
                                'status':1,
                                'status_detail':'active',
                            })        
                            sub_query2 = Q(**{
                                'user_object_exact': user,
                            })                           
                            query = reduce(operator.or_, [sub_query1,sub_query2])
                        else:
                            if not allow_user_search:
                                query = Q(**{
                                    'user_object_exact': user,
                                    'status':1,
                                    'status_detail':'active',
                                })
                            else:
                                sub_query1 = Q(**{
                                    'hide_in_search': False,
                                    'status':1,
                                    'status_detail':'active',
                                })        
                                sub_query2 = Q(**{
                                    'user_object_exact': user,
                                })                           
                                query = reduce(operator.or_, [sub_query1,sub_query2])
                        sqs = sqs.filter(query)
                    else: # anonymous
                        if not allow_user_search or not allow_anonymous_search:
                            return sqs.none()
                        query = Q(**{
                            'hide_in_search': False,
                            'status':1,
                            'status_detail':'active',
                        })  
                        sqs = sqs.filter(query)
            else: # anonymous
                if not allow_user_search or not allow_anonymous_search:
                    return sqs.none()
                query = Q(**{
                    'hide_in_search': False,
                    'status':1,
                    'status_detail':'active',
                })  
                sqs = sqs.filter(query)

        sqs = sqs.order_by('-create_dt')
        return sqs.models(self.model)