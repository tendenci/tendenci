from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.safestring import mark_safe

#from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from .models import Activity


class ActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'edit_link', 'user_profile',
                    'activity_name',
                    'start_date',
                    'end_date',
                    'status_detail']
    list_filter = ['status_detail', 'user']
    search_fields = ['user', 'activity_name']
    fieldsets = (
        ('', {
            'fields': ('user',
                        'activity_name',
                        'start_date',
                        'end_date',
                )
        }),
        (_('Status'), {'fields': (
            'status_detail',
            )}),
        )
    list_display_links = ('edit_link', )
    ordering = ['-id']

    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
        instance.owner = request.user
        instance.owner_username = request.user.username
        instance.save()
        return instance

    @mark_safe
    def user_profile(self, instance):
        return '<a href="{}">{}</a>'.format(
              reverse('profile', args=[instance.user.username]),
              instance.user.get_full_name() or instance.user.username)
    user_profile.short_description = _('User Profile')
    user_profile.admin_order_field = 'user__last_name' 

    def edit_link(self, obj):
        return "Edit"
    edit_link.short_description = _('edit') 

admin.site.register(Activity, ActivityAdmin)
