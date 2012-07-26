from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri
from django.conf import settings

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.products.models import Product, ProductFile, Category, Subcategory
from tendenci.apps.products.forms import ProductForm

class ProductFileAdmin(admin.StackedInline):
    model = ProductFile
    fieldsets = (
        (None, {
            'fields': (
            'file',
            'photo_description',
            'position',
        )},),
    )
    extra = 1

class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]

class ProductAdmin(TendenciBaseModelAdmin):
    list_display = ['name', 'slug','item_number', 'tags']
    list_filter = ['category', 'subcategory']
    search_fields = ['name', 'description', 'category__name', 'subcategory__name']
    inlines = [ProductFileAdmin,]
    fieldsets = (
        (None, 
            {'fields': (
                'name',
                'slug',
                'brand',
                'url',
                'item_number',
                'category',
                'subcategory',
                'summary',
                'description',
                'tags',
            )}
        ),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',),'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Publishing Status', {'fields': (
            'status',
            'status_detail'
        )}),
    )
    prepopulated_fields = {'slug': ['name']}
    form = ProductForm
    actions = []
    
    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )

    def save_formset(self, request, form, formset, change):
        for f in formset.forms:
            file = f.save(commit=False)
            if file.file:
                file.product = form.save()
                file.content_type = ContentType.objects.get_for_model(file.product)
                file.object_id = file.product.pk
                file.name = file.file.name
                file.creator = request.user
                file.owner = request.user
                file.save(log=False)
        
        formset.save()

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
