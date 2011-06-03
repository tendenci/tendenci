from django.contrib import admin
from before_and_after.models import BeforeAndAfter, Category, \
    Subcategory, PhotoSet
from before_and_after.forms import BnAForm

class PhotoSetAdmin(admin.TabularInline):
    model = PhotoSet
    extra = 1
    ordering = ("position",)

class BnAAdmin(admin.ModelAdmin):
    form = BnAForm
    inlines = [PhotoSetAdmin,]
    fieldsets = [('', {
                      'fields': [
                        'title',
                        'category',
                        'subcategory',
                        'description',
                        'tags'
                      ],
                      }),
                     ('Administrator Only', {
                      'fields': ['admin_notes',], 
                      'classes': ['admin-only',],
                    })]

admin.site.register(BeforeAndAfter, BnAAdmin)
admin.site.register(Category)
admin.site.register(Subcategory)
