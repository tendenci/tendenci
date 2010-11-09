from django.contrib import admin
from django.conf import settings
from user_groups.models import Group
from event_logs.models import EventLog
from perms.models import ObjectPermission 
from memberships.models import MembershipType, App, AppField
from memberships.forms import MembershipTypeForm, AppForm


class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'admin_fee', 'group', 'require_approval',
                     'renewal', 'expiration_method', 'corporate_membership_only',
                     'admin_only', 'status_detail']
    list_filter = ['name', 'price']
    
    fieldsets = (
        (None, {'fields': ('name', 'price', 'admin_fee', 'description', 'group')}),
        ('Expiration Method', {'fields': (('type_exp_method'),)}),

        ('Other Options', {'fields': (
            'corporate_membership_only','corporate_membership_type_id',
            'require_approval','renewal','renewal_period_start', 
            'renewal_period_end', 'expiration_grace_period', 
            'admin_only', 'order', 'status', 'status_detail')}),
    )

    form = MembershipTypeForm
    
    class Media:
        js = ("%sjs/jquery-1.4.2.min.js" % settings.STATIC_URL, 
              "%sjs/membtype.js" % settings.STATIC_URL,)
        
    
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
        
        # save the expiration method fields
        type_exp_method = form.cleaned_data['type_exp_method']
        type_exp_method_list = type_exp_method.split(",")
        for i, field in enumerate(form.type_exp_method_fields):
            if field=='fixed_expiration_rollover':
                if type_exp_method_list[i]=='':
                    type_exp_method_list[i] = ''
            else:
                if type_exp_method_list[i]=='':
                    type_exp_method_list[i] = "0"

            exec('instance.%s="%s"' % (field, type_exp_method_list[i]))
         
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
            
            # create a group for this type
            group = Group()
            group.name = instance.name
            # TODO:  a unique slug
            group.label = instance.name
            group.email_recipient = request.user.email
            group.show_as_option = 0
            group.allow_self_add = 0
            group.allow_self_remove = 0
            group.description = "Auto-generated with the membership type. Used membership only"
            group.notes = "Auto-generated with the membership type. Used membership only"
            group.use_for_membership = 1
            
            group.creator = request.user
            group.creator_username = request.user.username
            group.owner = request.user
            group.owner_username = request.user.username
            
            group.save()
            
            instance.group = group
 
        # save the object
        instance.save()
        
        #form.save_m2m()
        
        return instance

class AppFieldAdmin(admin.TabularInline):
    model = AppField

class AppAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name','slug', 'notes', ('use_captcha', 'require_login'))},),
        ('Administrative', {'fields': ('allow_anonymous_view','user_perms','group_perms','status','status_detail')}),
    )

    class Meta:
        js = [
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/admin/jquery-ui-1.8.2.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/dynamic-inlines-with-sorth.js' % settings.STATIC_URL,
        ]
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL], }

    inlines = (AppFieldAdmin,)
    prepopulated_fields = {'slug': ('name',)}
    form = AppForm

    def log_deletion(self, request, object, object_repr):
        super(AppAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 653000,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(AppAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 652000,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(AppAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 651000,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name, object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)

    def save_model(self, request, object, form, change):
        app = form.save(commit=False)

        # set up user permission
        app.allow_user_view, app.allow_user_edit = form.cleaned_data['user_perms']
        
        # adding the helpfile
        if not change:
            app.creator = request.user
            app.creator_username = request.user.username
            app.owner = request.user
            app.owner_username = request.user.username
 
        # save the object
        app.save()
        form.save_m2m()

        # permissions
        if not change:
            # assign permissions for selected groups
            ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], app)
            # assign creator permissions
            ObjectPermission.objects.assign(app.creator, app) 
        else:
            # assign permissions
            ObjectPermission.objects.remove_all(app)
            ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], app)
            ObjectPermission.objects.assign(app.creator, app) 
        
        return app

admin.site.register(MembershipType, MembershipTypeAdmin)
admin.site.register(App, AppAdmin)










