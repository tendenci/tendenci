from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.addons.resumes.models import Resume
from tendenci.addons.resumes.forms import ResumeForm

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
                       'skills',
                       'location',
                       'contact_email',
                       'contact_website',
                       'tags',
                       'activation_dt',
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
    form = ResumeForm
    ordering = ['-update_dt']

    def get_form(self, request, obj=None, **kwargs):
      FormModel = super(ResumeAdmin, self).get_form(request, obj, **kwargs)
      FormModel.user = request.user
      return FormModel

admin.site.register(Resume, ResumeAdmin)
