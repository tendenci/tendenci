from django.contrib import admin
from subscribers.models import GroupSubscription, SubscriberData

class DataAdmin(admin.TabularInline):
    model = SubscriberData
    ordering = ("field_label",)

class GroupSubAdmin(admin.ModelAdmin):
    inlines = (DataAdmin,)
    
admin.site.register(GroupSubscription, GroupSubAdmin)
