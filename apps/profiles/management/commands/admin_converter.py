from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group as Auth_Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db.models import Q

class Command(BaseCommand):

    def handle(self, *args, **options):
        """ admin was determined by: is_superuser=True and is_staff=False 
            now we changed criteria to be: is_superuser=False and is_staff=True
            This command is to convert all admins on the site to use the new criteria
            and add them to the auth group
        """
        # command to run: python manage.py admin_converter
        from profiles.utils import user_add_remove_admin_auth_group
        
        if hasattr(settings, 'ADMIN_AUTH_GROUP_NAME'):
            name = settings.ADMIN_AUTH_GROUP_NAME
        else:
            name = 'Admin'
        
        try:
            auth_group = Auth_Group.objects.get(name=name)
        except Auth_Group.DoesNotExist:
            auth_group = Auth_Group(name=name)
            auth_group.save()
        
            # assign permission to group, but exclude the auth content
            content_to_exclude = ContentType.objects.filter(app_label='auth')    
            permissions = Permission.objects.all().exclude(content_type__in=content_to_exclude)
            auth_group.permissions = permissions
            auth_group.save()
            print 'Successfully added admin auth group "%s".' % name
        
        print "Adding users (admins) to admin auth group...\n"

        count = 0
        
        # all admins (under the new criteria or old criteria). make sure they are on admin group
        users = User.objects.filter(Q(is_superuser=False, is_staff=True) 
                                    | Q(is_superuser=True, is_staff=False))
        if users:
            for user in users:
                if user.is_superuser and not user.is_staff:
                    user.is_superuser = False
                    user.is_staff = True
                    user.save()
                
                group_updated = False
                user_auth_groups = user.groups.all()
                if user_auth_groups:
                    if auth_group not in user_auth_groups:
                        user_auth_groups.append(auth_group)
                        user.groups = user_auth_groups
                        group_updated = True      
                else:
                    user.groups = [auth_group]
                    group_updated = True
                    
                if group_updated:
                    user.save()
                    count += 1
                    print 'User "%s(%s)" -- added' % (user.get_full_name(), user.username)
            print
        
        if count == 1:
            print '1 user added.'
        else:
            print '%d users added.' % count
        