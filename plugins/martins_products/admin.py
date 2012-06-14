from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri
from django.conf import settings
from django.contrib.contenttypes import generic

from event_logs.models import EventLog
from perms.utils import update_perms_and_save
from martins_products.models import Product, Formulation
from martins_products.forms import ProductForm
from categories.models import Category, CategoryItem

class CategoryItemInline(generic.GenericTabularInline):
    model = CategoryItem

class ProductAdmin(admin.ModelAdmin):
    list_display = [u'product_id', 'view_on_site', 'edit_link', 'tags']
    list_filter = []
    search_fields = []
    prepopulated_fields = {'product_slug': ['product_name']}
    actions = []
    inlines = [CategoryItemInline]
    form = ProductForm
    
    fieldsets = [('Product Information', {
                      'fields': ['product_id',
                                 'product_name',
                                 'product_slug',
                                 'product_code',
                                 'product_features',
                                 'product_specs',
                                 'brand',
                                 'generic_description',
                                 'category_num',
                                 'formulation',
                                 'active_ingredients',
                                 'key_insects',
                                 'use_sites',
                                 'msds_label',
                                 'product_label',
                                 'state_registered',
                                 'tags',
                                 'photo_upload'
                                ]
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['status',
                                 'status_detail'], 
                      'classes': ['admin-only'],
                    })]
    
    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            '%sjs/jquery-1.6.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery-ui-1.8.2.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/admin-list-reorder.js' % settings.STATIC_URL,
        )
    
    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:martins_products_product_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'

    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('products.detail', args=[obj.product_slug]),
            obj,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'

    def log_deletion(self, request, object, object_repr):
        super(ProductAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 1150300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(ProductAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 1150200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(ProductAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 1150100,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name, 
                                                   object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
                     
    def get_form(self, request, obj=None, **kwargs):
        """
        Category id field can only be viewed by superusers.
        inject the user in the form.
        """
        # exclude category_id field for users that are not superusers
        self.exclude = []
        if not request.user.is_superuser:
			self.exclude.append('category_id')
        form = super(ProductAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        
        return form

    def save_model(self, request, object, form, change):
        """
        update the permissions backend
        """
        instance = form.save(commit=False)
        perms = update_perms_and_save(request, form, instance)
        return instance

    def change_view(self, request, object_id, extra_context=None):
        result = super(ProductAdmin, self).change_view(request, object_id, extra_context)

        if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

admin.site.register(Product, ProductAdmin)
admin.site.register(Formulation)
