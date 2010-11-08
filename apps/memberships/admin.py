from django.contrib import admin
from memberships.models import MembershipType
from memberships.forms import MembershipTypeForm

class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'admin_fee', 'group', 'require_approval',
                     'renewal', 'expiration_method', 'corporate_membership_only',
                     'admin_only', 'status_detail']
    list_filter = ['name', 'price']
    
    fieldsets = (
        (None, {'fields': ('name', 'price', 'admin_fee', 'description', 'group')}),
        ('Expiration Method', {'fields': (
            ('type_exp_method'),)}),
        ('Other Options', {'fields': (
            'corporate_membership_only','corporate_membership_type_id',
            'require_approval','renewal','renewal_period_start', 
            'renewal_period_end', 'expiration_grace_period', 
            'admin_only', 'order',
            'status', 'status_detail')}),
    )
    
    form = MembershipTypeForm
    
    class Media:
        js = ("js/admin/jquery-1.4.2.min.js", "js/admin/membtype.js",)
        
    
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
        
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
            
        # TODO: handle the expiration method here
 
        # save the object
        instance.save()
        #form.save_m2m()
        
        return instance

class MembershipApplicationAdmin(admin.ModelAdmin):

    fieldsets = (
        (None,
            {
                'fields': (
                    'name','slug', 'notes', 'use_captcha', 'require_login',
                )
            },
        ),
    )

    prepopulated_fields = {'slug': ('name',)}
    form = MembershipApplicationForm

class MembershipApplicationPageAdmin(admin.ModelAdmin):
    list_display = ('ma', 'sort_order',)

class MembershipApplicationSectionAdmin(admin.ModelAdmin):
    list_display = ('ma', 'ma_page', 'label', 'description', 'admin_only', 'order', 'css_class')

class MembershipApplicationFieldAdmin(admin.ModelAdmin):
    list_display = ('ma', 'ma_section', 'object_type', 'label', 'field_name', 'field_type', 'size',
        'choices', 'required', 'visible', 'admin_only', 'editor_only', 'order', 'css_class',
    )

admin.site.register(MembershipType, MembershipTypeAdmin)
admin.site.register(MembershipApplication, MembershipApplicationAdmin)
admin.site.register(MembershipApplicationPage, MembershipApplicationPageAdmin)
admin.site.register(MembershipApplicationSection, MembershipApplicationSectionAdmin)
admin.site.register(MembershipApplicationField, MembershipApplicationFieldAdmin)
