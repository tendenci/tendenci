from django.contrib import admin


class SettingAdmin(admin.ModelAdmin):
    list_display = ['name','label','value','scope','scope_category']
    search_fields = ['name','label']
    list_filter = ['scope_category']

    fieldsets = (
        (None, {'fields': ('value',)}),
    )

    def queryset(self, request):
        qs = super(SettingAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(client_editable=True)

class SettingAdminDev(admin.ModelAdmin):
    list_display = ['name','label','value','scope','scope_category']
    search_fields = ['name','label']
    list_filter = ['scope_category']

# admin.site.register(Setting, SettingAdminDev)
