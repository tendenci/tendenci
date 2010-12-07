from django.contrib import admin
from django.conf import settings

from corporate_memberships.models import CorporateMembershipType
from corporate_memberships.models import CorpApp, CorpAppPage, CorpAppSection, CorpField, CorpAppField
from corporate_memberships.forms import CorporateMembershipTypeForm, CorpAppPageForm, CorpAppSectionForm, \
                                        CorpAppFieldForm, CorpAppForm

class CorporateMembershipTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'renewal_price', 'membership_type',  
                     'admin_only', 'status_detail', 'order']
    list_filter = ['name', 'price', 'status_detail']
    
    fieldsets = (
        (None, {'fields': ('name', 'price', 'renewal_price', 'membership_type', 'description')}),
        ('Individual Pricing Options', {'fields': ('apply_threshold', 'individual_threshold',
                                                   'individual_threshold_price',)}),
        ('Other Options', {'fields': (
            'order', ('admin_only', 'status'), 'status_detail')}),
    )
    
    form = CorporateMembershipTypeForm
    
    
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
         
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
 
        # save the object
        instance.save()
        
        #form.save_m2m()
        
        return instance

class CorpAppPageAdmin(admin.ModelAdmin):
    list_display = ['order', 'title']
    form = CorpAppPageForm
    
#    class Media:
#        js = (
#            '%sjs/admin/RelatedObjectLookups_cma.js' % settings.STATIC_URL,
#        )

admin.site.register(CorpAppPage, CorpAppPageAdmin)
  
class CorpAppSectionAdmin(admin.ModelAdmin):
    list_display = ['label', 'admin_only']
    form = CorpAppSectionForm

admin.site.register(CorpAppSection, CorpAppSectionAdmin)

class CorpAppFieldAdmin(admin.ModelAdmin):
    list_display = ['label', 'field_name', 'field_type', 'choices', 'required', 'visible', 'admin_only']
    fieldsets = (
        (None, {'fields': ('label', 'field_name', 'field_type', 'choices', 'field_layout',
                ('required', 'no_duplicates', 'visible', 'admin_only'), 'size', 'default_value',
                'help_text', 'css_class')}),
    )
    form = CorpAppFieldForm

admin.site.register(CorpAppField, CorpAppFieldAdmin)


class FieldInline(admin.TabularInline):
#class FieldInline(admin.StackedInline):
    model = CorpField
    extra = 0
    #raw_id_fields = ("page", 'section', 'field') 
  
class CorpAppAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'use_captcha', 'require_login', 'status_detail']
    list_filter = ['name', 'status_detail']
    
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'corp_memb_type', 'authentication_method', 'notes')}),
        ('Other Options', {'fields': (
            ('use_captcha', 'require_login'), 'status', 'status_detail')}),
    )
    
    class Media:
        js = (
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/inline_ordering.js' % settings.STATIC_URL,
            #'%sjs/admin/RelatedObjectLookups_cma.js' % settings.STATIC_URL,
        )
        
    inlines = [FieldInline]
    prepopulated_fields = {'slug': ('name',)}
    form = CorpAppForm
    
    #radio_fields = {"corp_memb_type": admin.VERTICAL}
    
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
         
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
 
        # save the object
        instance.save()
        
        form.save_m2m()
        
        return instance


admin.site.register(CorporateMembershipType, CorporateMembershipTypeAdmin)
admin.site.register(CorpApp, CorpAppAdmin)