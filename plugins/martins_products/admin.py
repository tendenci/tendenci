from django.contrib import admin
from django.conf import settings

from perms.admin import TendenciBaseModelAdmin
from martins_products.models import Product, Formulation, Category
from martins_products.forms import ProductForm

class ProductAdmin(TendenciBaseModelAdmin):
    list_display = [u'product_id', 'product_name', 'tags']
    list_filter = []
    search_fields = []
    prepopulated_fields = {'product_slug': ['product_name']}
    actions = []
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
                                 'category',
                                 'formulation',
                                 'active_ingredients',
                                 'key_insects',
                                 'use_sites',
                                 'msds_label',
                                 'product_label',
                                 'state_registered',
                                 'tags',
                                 'photo_upload',
                                 'hover_photo_upload',
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

admin.site.register(Product, ProductAdmin)
admin.site.register(Formulation)
admin.site.register(Category)
