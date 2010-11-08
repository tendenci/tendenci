from django.contrib import admin

from memberships.models import MembershipType, MembershipApplication, \
MembershipApplicationPage, MembershipApplicationSection, MembershipApplicationField

from memberships.forms import MembershipTypeForm, MembershipApplicationForm, \
MembershipApplicationPageForm, MembershipApplicationSectionForm, \
MembershipApplicationFieldForm

class MembershipTypeAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,
            {
                'fields': (
                    'name','description', 'price', 'admin_fee', 'group',
                    'require_approval', 'renewal', 'order', 'ma',
                )
            },
        ),
        ('Period',
            {
                'fields': ('period', 'period_unit', 'period_type'),
            },
        ),
        ('Expiration',
            {
                'fields': ('expiration_method', 'expiration_method_day', 'expiration_grace_period'),
            },
        ),
        ('Renew Expiration',
            {
                'fields': ('renew_expiration_method', 'renew_expiration_day',),
            },
        ),
        ('Fixed Expiration',
            {
                'fields': ('fixed_expiration_method', 'fixed_expiration_day', 
                    'fixed_expiration_month', 'fixed_expiration_year', 
                    'fixed_expiration_rollover', 'fixed_expiration_rollover_days',
                ),
            },
        ),
        ('Renewal Period',
            {
                'fields': ('renewal_period_start','renewal_period_end',),
            },
        ),
        ('Corporate Membership',
            {
                'fields': ('corporate_membership_only','corporate_membership_type_id',),
            },
        ),
        ('Administrative',
            {
                'fields': ('allow_anonymous_view','user_perms','group_perms','status','status_detail'),
            },
        ),
    )

    form = MembershipTypeForm

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



