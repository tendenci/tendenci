from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group as Auth_Group, Permission, User
from django.contrib.contenttypes.models import ContentType
#from profiles.models import Profile

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        """ admin was determined by: is_superuser=True and is_staff=False 
            now we changed criteria to be: is_superuser=False and is_staff=True
            This command is to convert all admins on the site to use the new criteria
            and add them to the auth group
        """
        # command to run: python manage.py admin_converter
        
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
        
        users = User.objects.filter(is_superuser=True, is_staff=False)
        if users:
            # get admin auth group
            for user in users:
                print 'Converting user "%s"' % user.username
                user.is_superuser = False
                user.is_staff = True
                user.groups = [auth_group]
                
                user.save()
            print 'Successfully converted all admins with the new criteria.'
        else:
            print 'No admins need to be converted.'