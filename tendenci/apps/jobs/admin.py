import copy

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.jobs.models import Job, JobPricing
from tendenci.apps.jobs.forms import JobAdminForm, JobPricingForm
from tendenci.apps.jobs.models import Category as JobCategory


class JobAdmin(TendenciBaseModelAdmin):
    list_display = ['title', 'post_dt', 'cat', 'sub_cat', 'owner_link', 'admin_perms', 'admin_status']
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
         (_('Category'), {
            'fields': ['cat',
                       'sub_cat'
                       ],
            'classes': ['boxy-grey job-category'],
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
    ordering = ['-post_dt', '-update_dt']

    def get_form(self, request, obj=None, **kwargs):
        form = super(JobAdmin, self).get_form(request, obj=None, **kwargs)
        form.user = request.user
        return form


admin.site.register(Job, JobAdmin)


class JobPricingAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'duration',
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
    fields = copy.copy(list_display).remove('id')

    form = JobPricingForm

admin.site.register(JobPricing, JobPricingAdmin)


class CategoryAdminInline(admin.TabularInline):
    fieldsets = ((None, {'fields': ('name', 'slug')}),)
    prepopulated_fields = {'slug': ['name']}
    model = JobCategory
    extra = 0
    verbose_name = _("Job Sub-Category")
    verbose_name_plural = _("Job Sub-Categories")
    ordering = ['name']


class JobCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'sub_categories',
        'slug',
    ]
    list_display_links = ('name', )
    inlines = (CategoryAdminInline,)
    prepopulated_fields = {'slug': ['name']}
    fieldsets = ((None, {'fields': ('name', 'slug')}),)

    @mark_safe
    def sub_categories(self, instance):
        return ', '.join(JobCategory.objects.filter(parent=instance).values_list('name', flat=True))

    def get_queryset(self, request):
        qs = super(JobCategoryAdmin, self).get_queryset(request)
        return qs.filter(parent__isnull=True)

admin.site.register(JobCategory, JobCategoryAdmin)
