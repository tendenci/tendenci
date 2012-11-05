from django.contrib import admin

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.addons.jobs.models import Job
from tendenci.addons.jobs.forms import JobForm

class JobAdmin(TendenciBaseModelAdmin):
    list_display = ['title', 'post_dt', 'owner_link', 'admin_perms', 'admin_status']
    list_filter = ['status_detail', 'owner_username']
    prepopulated_fields = {'slug': ['title']}
    search_fields = ['title', 'description']
    fieldsets = (
        ('Job Information', {
            'fields': ('title',
                'slug',
                'description',
                'group',
                'skills',
                'location',
                'contact_email',
                'contact_website',
                'tags',
                'post_dt',
                )
        }),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
            )}),
        ('Status', {'fields': (
            'status',
            'status_detail',
            )}),
    )
    form = JobForm
    ordering = ['-update_dt']

admin.site.register(Job, JobAdmin)
