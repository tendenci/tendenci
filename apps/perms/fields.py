from django.forms import ModelMultipleChoiceField
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.query import QuerySet

from perms.models import ObjectPermission

__ALL__ = ('UserPermissionField','users_with_perms','user_perm_queryset',)

user_perm_options = {
    'label':'People',
    'help_text':'People who have admin permissions',
    'required':False,
    'queryset': User.objects.filter(is_active=True),                   
}

def user_perm_queryset(user_or_users):
    """
        Create a users queryset that does not include 
        a specified user or list of users
    """
    multi_user = False
    if isinstance(user_or_users,list):
        multi_user = True
    if isinstance(user_or_users,QuerySet):
        multi_user = True

    if multi_user:
        pks = [u.id for u in user_or_users]
        user_qs = User.objects.filter(Q(is_active=True) & ~Q(pk__in=pks))
    else:
        user_qs = User.objects.filter(Q(is_active=True) & ~Q(pk=user_or_users.pk))
    return user_qs
    
def users_with_perms(instance):
    """
        Return a list of users that have permissions
        on a model instance. 
    """
    content_type = ContentType.objects.get_for_model(instance)
    filters = {
        'user__in': User.objects.filter(is_active=True),
        'content_type':content_type,
        'object_id':instance.pk       
    }
    users = ObjectPermission.objects.filter(**filters)
    return list(set([u.user.pk for u in users]))  
        
class UserPermissionField(ModelMultipleChoiceField): 
    """
        Inherits from ModelMultipleChoiceField and
        sets some default meta data
    """
    def __init__(self, *args, **kwargs):
        kwargs.update(user_perm_options)
        super(UserPermissionField, self).__init__(*args, **kwargs)