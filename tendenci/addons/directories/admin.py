from django.contrib import admin
from tendenci.core.registry import admin_registry
from tendenci.addons.directories.models import Directory

class DirectoryAdmin(admin.ModelAdmin):
    list_display = ['headline','create_dt']

#admin_registry.site.register(Directory, DirectoryAdmin)