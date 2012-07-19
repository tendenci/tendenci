from django.contrib import admin

# Add your admin site registrations here, eg.
from perms.object_perms import ObjectPermission
from user_groups.models import Group, GroupMembership
from user_groups.forms import GroupAdminForm

class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'show_as_option','allow_self_add','allow_self_remove']
    search_fields = ['name','label']
    fieldsets = (
        (None, {'fields': ('name', 'label', 'entity', 'email_recipient', 'permissions')}),
        ('Flags', {'fields': (
            'show_as_option', 'allow_self_add', 'allow_self_remove')}),
        ('Administrative', {'fields': (
            'allow_anonymous_view','user_perms','status','status_detail' )}),
    )    
    form = GroupAdminForm

    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)

        # set up user permission
        instance.allow_user_view, instance.allow_user_edit = form.cleaned_data['user_perms']
        
        # adding the helpfile
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
        
        # save the object
        instance.save()
        form.save_m2m()
        
        return instance


class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['group', 'member']
    search_fields = ['group','member']
    fieldsets = (
        (None, {'fields': ('group', 'member')}),
    )    

admin.site.register(Group, GroupAdmin)
#admin.site.register(GroupMembership, GroupMembershipAdmin)