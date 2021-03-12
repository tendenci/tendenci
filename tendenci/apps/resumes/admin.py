from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.resumes.models import Resume
from tendenci.apps.resumes.forms import ResumeForm

class ResumeAdmin(TendenciBaseModelAdmin):
    list_display = ['title', 'activation_dt', 'owner_link', 'admin_perms', 'admin_status']
    list_filter = ['status_detail', 'owner_username']
    prepopulated_fields = {'slug': ['title']}
    search_fields = ['title', 'description']
    fieldsets = (
        (_('Resume Information'), {
            'fields': ('title',
                     'slug',
                     'description',
                     'resume_url',
                     'resume_file',
                     'industry',
                     'location',
                     'skills',
                     'experience',
                     'awards',
                     'education',
                     'tags',
                     'requested_duration',
                     'is_agency'
                )
        }),
        (_('Contact'), {
          'fields': ('first_name',
                     'last_name',
                     'contact_address',
                     'contact_address2',
                     'contact_city',
                     'contact_state',
                     'contact_zip_code',
                     'contact_country',
                     'contact_phone',
                     'contact_phone2',
                     'contact_fax',
                     'contact_email',
                     'contact_website',
                     ),
            'classes': ['contact'],
          }),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
            )}),
        (_('Administrator Only'), {
              'fields': ['activation_dt',
                         'expiration_dt',
                         'syndicate',
                         'status_detail'],
              'classes': ['admin-only'],
            })
        )
    form = ResumeForm
    ordering = ['-update_dt']

    def get_form(self, request, obj=None, **kwargs):
        FormModel = super(ResumeAdmin, self).get_form(request, obj, **kwargs)
        FormModel.user = request.user
        return FormModel

admin.site.register(Resume, ResumeAdmin)
