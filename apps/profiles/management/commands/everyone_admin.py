from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group as Auth_Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db.models import Q

class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Created for self signup use. Initially everyone in the database is an administrator.
        We create the 'admin' group if it doesn't exist
        We set the appropriate permissions on the user
        We put the user in the admin group
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

        users = User.objects.all()

        for u in users:
            u.is_staff = True
            u.is_superuser = False
            u.save()

            user_auth_groups = u.groups.all()

            if auth_group not in user_auth_groups:
                user_auth_groups.append(auth_group)
                user.groups = user_auth_groups
            else:
                user.groups = [auth_group]

            user.save()
            count += 1
            print 'User "%s(%s)" -- added' % (u.get_full_name(), u.username)
        
        if count == 1:
            print "1 user added"
        else:
            print "%d users added" % count