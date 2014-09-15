from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.educations.models import Education
from tendenci.apps.educations.forms import EducationForm


class EducationAdmin(TendenciBaseModelAdmin):
    list_display = ['user', 'school', 'major', 'degree',
                    'graduation_dt',
                    'owner_link', 'admin_perms',
                    'admin_status']
    list_filter = ['status_detail', 'owner_username']
    search_fields = ['school', 'user']
    fieldsets = (
        ('', {
            'fields': ('user',
                        'school',
                        'major',
                        'degree',
                        'graduation_dt',
                )
        }),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
            )}),
        (_('Status'), {'fields': (
            'status',
            'status_detail',
            )}),
        )
    form = EducationForm
    ordering = ['-update_dt']

admin.site.register(Education, EducationAdmin)
