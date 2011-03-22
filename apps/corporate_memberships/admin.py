from django.contrib import admin
from django.conf import settings

from corporate_memberships.models import CorporateMembershipType
from corporate_memberships.models import CorpApp, CorpField
from corporate_memberships.forms import CorporateMembershipTypeForm, CorpFieldForm, CorpAppForm
from corporate_memberships.utils import get_corpapp_default_fields_list, update_authenticate_fields, edit_corpapp_update_memb_app

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


#class FieldInline(admin.TabularInline):
class FieldInline(admin.StackedInline):
    model = CorpField
    extra = 0
    form = CorpFieldForm
    fieldsets = (
        (None, {'fields': (('label', 'field_type'),
        ('choices', 'field_layout'), 'size', ('required', 'visible', 'no_duplicates', 'admin_only'), 
            'instruction', 'default_value', 'css_class', 'order')}),
    )
    #raw_id_fields = ("page", 'section', 'field') 
    template = "corporate_memberships/admin/stacked.html"
  
class CorpAppAdmin(admin.ModelAdmin):
    def corp_app_form_link(self):
        return '<a href="%s">%s</a>' % (self.get_absolute_url(), self.slug)
    corp_app_form_link.allow_tags = True
    
    list_display = ['name', corp_app_form_link, 'status_detail']
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
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            #'%sjs/admin/corpapp.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/corpapp-inline.css' % settings.STATIC_URL], }
        
    inlines = [FieldInline]
    prepopulated_fields = {'slug': ('name',)}
    form = CorpAppForm
    add_form_template = "corporate_memberships/admin/add_form.html"
    
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
        # exclude fields for corporate_membership_type and payment_method
        excluded_lines = [2, 3]  # exclude lines in inline field_set - 'choices', 'field_layout', 'size' 
        excluded_fields = ['field_type', 'no_duplicates', 'admin_only']
        fields_to_check = ['corporate_membership_type', 'payment_method']
        if extra_context:
            extra_context.update({
                                  'excluded_lines': excluded_lines,
                                  "excluded_fields":excluded_fields,
                                  'fields_to_check': fields_to_check
                                  })
        else:
            extra_context = {'excluded_lines': excluded_lines,
                             "excluded_fields":excluded_fields,
                             'fields_to_check': fields_to_check}
        return super(CorpAppAdmin, self).change_view(request, object_id,
                                              extra_context)
         
    def get_fieldsets(self, request, obj=None):
        if obj and obj.id:
            return  (
                        (None, {'fields': ('name', 'slug', 'corp_memb_type', 'authentication_method', 
                                           'memb_app', 'description', 'confirmation_text', 'notes')}),
                        ('Other Options', {'fields': (
                            'status', 'status_detail')}),
                    ) 
        else:
            return (
                        (None, {'fields': ('name', 'slug', 'corp_memb_type', 'authentication_method', 
                                           'memb_app', 'description', 'confirmation_text', 'notes')}),
                        ('Other Options', {'fields': (
                             'status', 'status_detail')}),
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
            # set some default fields to the app
            fields_list = get_corpapp_default_fields_list()
            if fields_list:
                for field_d in fields_list:
                    field_d.update({'corp_app':instance})
                    f = CorpField(**field_d)
                    f.save()
                                    
        form.save_m2m()
        
        #if change:
        update_authenticate_fields(instance)
        edit_corpapp_update_memb_app(instance)
        
        return instance


admin.site.register(CorporateMembershipType, CorporateMembershipTypeAdmin)
admin.site.register(CorpApp, CorpAppAdmin)