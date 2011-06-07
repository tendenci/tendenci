from django.contrib import admin
from django.conf import settings

from before_and_after.models import BeforeAndAfter, Category, \
    Subcategory, PhotoSet
from before_and_after.forms import BnAForm

class PhotoSetAdmin(admin.StackedInline):
    model = PhotoSet
    extra = 1
    ordering = ("order",)

class BnAAdmin(admin.ModelAdmin):
    form = BnAForm
    inlines = [PhotoSetAdmin,]
    
    fieldsets = (
        (None, {'fields': (
            'title',
            'category',
            'subcategory',
            'description',
            'tags',
        )}),
        ('Administrative', {'fields': (
            'allow_anonymous_view',
            'status',
            'status_detail',
            'admin_notes',
        )}),
    )
            
    class Media:
        js = (
            '%sjs/admin/sortable_inline/jquery-1.5.1.min.js' % settings.STATIC_URL,
            '%sjs/admin/sortable_inline/jquery-ui-1.8.13.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/sortable_inline/stacked-sort.js' % settings.STATIC_URL,
        )
    
admin.site.register(BeforeAndAfter, BnAAdmin)
admin.site.register(Category)
admin.site.register(Subcategory)
