from django.contrib import admin
from django.conf import settings

from perms.admin import TendenciBaseModelAdmin
from before_and_after.models import BeforeAndAfter, Category, \
    Subcategory, PhotoSet
from before_and_after.forms import BnAForm

class PhotoSetAdmin(admin.StackedInline):
    model = PhotoSet
    extra = 1
    
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "warning"]
    list_filter = ["category", "warning"]

class BnAAdmin(TendenciBaseModelAdmin):
    list_display = ["title", "category", "subcategory", 'admin_notes','ordering']
    list_filter = ["category", "subcategory"]
    form = BnAForm
    ordering = ['-ordering']
    list_editable = ['ordering']
    inlines = [PhotoSetAdmin,]
    
    fieldsets = (
        (None, {'fields': (
            'title',
            'category',
            'subcategory',
            'description',
            'tags',
            'admin_notes',
        )}),
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

    class Media:
        js = (
            '%sjs/admin/sortable_inline/jquery-1.5.1.min.js' % settings.STATIC_URL,
            '%sjs/admin/sortable_inline/jquery-ui-1.8.13.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/sortable_inline/stacked-sort.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            '%sjs/jquery-1.6.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery-ui-1.8.2.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/admin-list-reorder.js' % settings.STATIC_URL,
        )

admin.site.register(BeforeAndAfter, BnAAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
