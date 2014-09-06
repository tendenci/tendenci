from django.contrib import admin

from tendenci.apps.perms.admin import TendenciBaseModelAdmin

from tendenci.apps.announcements.forms import EmergencyAnnouncementAdminForm
from tendenci.apps.announcements.models import EmergencyAnnouncement


class EmergencyAnnouncementAdmin(TendenciBaseModelAdmin):

    list_display = ['title', 'enabled']
    form = EmergencyAnnouncementAdminForm
    fieldsets = (
        (None, {'fields': ('title', 'content', 'enabled')}),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
    )

admin.site.register(EmergencyAnnouncement, EmergencyAnnouncementAdmin)

