from django.contrib import admin

from tendenci.apps.categories.models import Category


class CategoryAdmin(admin.ModelAdmin):
    #model = Category
    list_display = ['id', 'name',]
    list_display_links = ['name']


admin.site.register(Category, CategoryAdmin)