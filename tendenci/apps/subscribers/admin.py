from django.contrib import admin
from tendenci.apps.subscribers.models import GroupSubscription, SubscriberData


class DataAdmin(admin.TabularInline):
    model = SubscriberData
    ordering = ("field_label",)


class GroupSubAdmin(admin.ModelAdmin):
    inlines = (DataAdmin,)

#admin.site.register(GroupSubscription, GroupSubAdmin)
