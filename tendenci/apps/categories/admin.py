from django.contrib import admin
from django.utils.safestring import mark_safe

from tendenci.apps.categories.models import Category, CategoryItem


class CategoryInlineAdmin(admin.TabularInline):
    model = CategoryItem
    fields = ['content_type', 'object_id',]
    fk_name = 'category'
    extra = 0
    max_num = 0

class SubCategoryInlineAdmin(admin.TabularInline):
    model = CategoryItem
    verbose_name = "Subcategory item"
    verbose_name_plural = "Subcategory items"
    fields = ['content_type', 'object_id',]
    fk_name = 'parent'
    extra = 0
    max_num = 0

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name',]
    list_display_links = ['name']
    ordering = ['name',]

    inlines = [CategoryInlineAdmin, SubCategoryInlineAdmin]


class CategoryItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'show_parent', 'content_type', 'show_object']
    list_filter = (('content_type', admin.RelatedOnlyFieldListFilter),
                   'category', )
    search_fields = ['category__name', 'parent__name']
    ordering = ['content_type', 'object_id']
    view_on_site = False

    def __init__(self,*args,**kwargs):
        super(CategoryItemAdmin, self).__init__(*args, **kwargs)
        admin.views.main.EMPTY_CHANGELIST_VALUE = '-'

    def has_add_permission(self, request):
        return False

    @mark_safe
    def show_parent(self, instance):
        return instance.parent
    show_parent.short_description = 'Subcategory'
    show_parent.admin_order_field = 'parent'

    @mark_safe
    def show_object(self, instance):
        if instance.content_type and instance.object_id:
            obj = instance.content_type.get_object_for_this_type(id=instance.object_id)
            if obj:
                return '<a href="{0}">{1}</a>'.format(
                        obj.get_absolute_url(),
                        instance.object,
                    )
        return ""
    show_object.short_description = u'Object'


admin.site.register(Category, CategoryAdmin)
admin.site.register(CategoryItem, CategoryItemAdmin)
