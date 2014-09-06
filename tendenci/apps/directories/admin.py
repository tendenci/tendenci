from django.contrib import admin
from tendenci.apps.directories.models import Directory


class DirectoryAdmin(admin.ModelAdmin):
    list_display = ['headline', 'create_dt']

# admin.site.register(Directory, DirectoryAdmin)
