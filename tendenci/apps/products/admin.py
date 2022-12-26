from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from .models import Product, ProductFile, Category
from .forms import ProductForm

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


class ProductAdminInline(admin.TabularInline):
    fieldsets = (
        (None, {
            'fields': (
            'name',
            'slug',
        )},),
    )
    prepopulated_fields = {'slug': ['name']}
    extra = 0
    model = Product


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', "name"]
    inlines = (ProductAdminInline,)


class ProductAdmin(TendenciBaseModelAdmin):
    list_display = ['name', 'category',]
    list_filter = ['category',]
    search_fields = ['name', 'description', 'category__name',]
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
    view_on_site = False


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
