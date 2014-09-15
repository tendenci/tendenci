from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.jobs.models import Job, JobPricing
from tendenci.apps.jobs.forms import JobAdminForm, JobPricingForm


class JobAdmin(TendenciBaseModelAdmin):
    list_display = ['title', 'post_dt', 'owner_link', 'admin_perms', 'admin_status']
    list_filter = ['status_detail', 'owner_username']
    prepopulated_fields = {'slug': ['title']}
    search_fields = ['title', 'description']
    fieldsets = (
        (_('Job Information'), {
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
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        (_('Status'), {'fields': (
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


class JobPricingAdmin(admin.ModelAdmin):
    list_display = [
        'duration',
        'title',
        'regular_price',
        'premium_price',
        'regular_price_member',
        'premium_price_member',
        'include_tax',
        'tax_rate',
        'show_member_pricing',
        'status'
    ]
    list_filter = ['status', 'include_tax']
    search_fields = ['title']
    ordering = ['-update_dt']
    fields = list_display

    form = JobPricingForm

admin.site.register(JobPricing, JobPricingAdmin)
