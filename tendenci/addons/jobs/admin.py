from django.contrib import admin

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.addons.jobs.models import Job
from tendenci.addons.jobs.forms import JobAdminForm


class JobAdmin(TendenciBaseModelAdmin):
    list_display = ['title', 'post_dt', 'owner_link', 'admin_perms', 'admin_status']
    list_filter = ['status_detail', 'owner_username']
    prepopulated_fields = {'slug': ['title']}
    search_fields = ['title', 'description']
    fieldsets = (
        ('Job Information', {
            'fields': (
                'title',
                'slug',
                'description',
                'group',
                'location',
                'skills',
                'experience',
                'education',
                'level',
                'period',
                'is_agency',
                'contact_method',
                'position_reports_to',
                'salary_from',
                'salary_to',
                'computer_skills',
                'job_url',
                'entity',
                'contact_company',
                'contact_name',
                'contact_address',
                'contact_address2',
                'contact_city',
                'contact_state',
                'contact_zip_code',
                'contact_country',
                'contact_phone',
                'contact_fax',
                'contact_email',
                'contact_website',
                'tags',
                'pricing',
                'post_dt',
                'activation_dt',
                'expiration_dt',
                'payment_method',
                'list_type',
            )
        }),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Status', {'fields': (
            'status_detail',
        )}),
    )
    form = JobAdminForm
    ordering = ['-update_dt']

    def get_form(self, request, obj=None, **kwargs):
        form = super(JobAdmin, self).get_form(request, obj=None, **kwargs)
        form.user = request.user
        return form


admin.site.register(Job, JobAdmin)
