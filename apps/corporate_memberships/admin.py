from django.contrib import admin
from django.conf import settings

from corporate_memberships.models import CorporateMembershipType
from corporate_memberships.models import CorpApp, CorpField
from corporate_memberships.forms import CorporateMembershipTypeForm, CorpFieldForm, CorpAppForm

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

#class CorpFieldAdmin(admin.ModelAdmin):
#    list_display = ['label', 'field_name', 'field_type', 'choices', 'required', 'visible', 'admin_only']
#    fieldsets = (
#        (None, {'fields': ('label', 'field_name', 'field_type', 'choices', 'field_layout',
#                ('required', 'no_duplicates', 'visible', 'admin_only'), 'size', 'default_value',
#                'instruction', 'css_class')}),
#    )
#    form = CorpFieldForm
#    #ordering = ['id']
    
#    class Media:
#        js = ("%sjs/jquery-1.4.2.min.js" % settings.STATIC_URL, 
#              "%sjs/corpfield.js" % settings.STATIC_URL,)

#admin.site.register(CorpField, CorpFieldAdmin)


#class FieldInline(admin.TabularInline):
class FieldInline(admin.StackedInline):
    model = CorpField
    extra = 0
    form = CorpFieldForm
    #raw_id_fields = ("page", 'section', 'field') 
  
class CorpAppAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'use_captcha', 'require_login', 'status_detail']
    list_filter = ['name', 'status_detail']
    
    #fieldsets = (
    #    (None, {'fields': ('name', 'slug', 'corp_memb_type', 'authentication_method', 'notes')}),
    #    ('Other Options', {'fields': (
    #        ('use_captcha', 'require_login'), 'status', 'status_detail')}),
    #)
    
    class Media:
        js = (
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/inline_ordering2.js' % settings.STATIC_URL,
            #'%sjs/admin/RelatedObjectLookups_cma.js' % settings.STATIC_URL,
        )
        
    inlines = [FieldInline]
    prepopulated_fields = {'slug': ('name',)}
    form = CorpAppForm
    
    #radio_fields = {"corp_memb_type": admin.VERTICAL}
    
    def add_view(self, request, form_url='', extra_context=None):
        self.inline_instances = []
        return super(CorpAppAdmin, self).add_view(request, form_url,
                                              extra_context) 
    
    def change_view(self, request, object_id, extra_context=None):
        self.inlines = [FieldInline]
        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)
        return super(CorpAppAdmin, self).change_view(request, object_id,
                                              extra_context)
         
    def get_fieldsets(self, request, obj=None):
        if obj and obj.id:
            return  (
                        (None, {'fields': ('name', 'slug', 'corp_memb_type', 'authentication_method', 'notes')}),
                        ('Other Options', {'fields': (
                            ('use_captcha', 'require_login'), 'status', 'status_detail')}),
                    ) 
        else:
            return (
                        (None, {'fields': ('name', 'slug', 'corp_memb_type', 'authentication_method', 'notes')}),
                        ('Other Options', {'fields': (
                            ('use_captcha', 'require_login'), 'status', 'status_detail')}),
                        ('Form Fields', {'fields':(), 
                                         'description': 'You will have the chance to add or manage the form fields later on editing.'}),
                    )

    
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
        set_default_fields = False
         
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
            set_default_fields = True
 
        # save the object
        instance.save()
        
        if set_default_fields:
            # set default fields to the app
            default_fields_d = {'Company Details': ['name', 'address', 'address2', 
                                                    'city', 'state', 'zipcode',
                                                    'phone', 'website'],
                                'Membership Details': ['corporate_membership_type'], 
                                'Admin Only': [],
                                'Payment Details': ['payment_method'],
                                'Representatives': ['dues_rep']}
            
#            i = 0
#            try:
#                page = CorpPage.objects.get(id=1)
#            except CorpPage.DoesNotExist:
#                page = None
#            for key in default_fields_d.keys():
#                if default_fields_d[key]:
#                    try:
#                        section = CorpSection.objects.get(label=key)
#                    except CorpSection.DoesNotExist:
#                        section = None
#            
#                    fields = CorpField.objects.filter(field_name__in=default_fields_d[key])
#            
#                    for field in fields:
#                        i = i + 1
#                        f = CorpAppField(cma=instance, page=page, section=section, field=field, order=i)
#                        f.save()
                        
        form.save_m2m()
        
        return instance


admin.site.register(CorporateMembershipType, CorporateMembershipTypeAdmin)
admin.site.register(CorpApp, CorpAppAdmin)