from django.contrib import admin
from tendenci.core.registry import admin_registry
from tendenci.apps.subscribers.models import GroupSubscription, SubscriberData

class DataAdmin(admin.TabularInline):
    model = SubscriberData
    ordering = ("field_label",)

class GroupSubAdmin(admin.ModelAdmin):
    inlines = (DataAdmin,)
    
#admin_registry.site.register(GroupSubscription, GroupSubAdmin)
