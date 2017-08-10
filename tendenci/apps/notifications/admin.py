from __future__ import print_function
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.notifications.models import (NoticeType, NoticeSetting, Notice,
    ObservedItem, NoticeEmail)


class NoticeTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'display', 'description', 'default')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return obj is None

    def __init__(self, *args, **kwargs):
        super(NoticeTypeAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )


class NoticeSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'notice_type', 'medium', 'send')


class NoticeAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'notice_type', 'added', 'unseen', 'archived')


class NoticeEmailAdmin(admin.ModelAdmin):
    list_display = ('preview_email', 'date_sent')
    actions = ['resend']

    def has_add_permission(self, request):
        return False

    def has_view_permission(self, request, obj=None):
        return False

    def preview_email(self, obj):
        return '<a href="%s">%s</a>' % \
            (reverse('notification_email', args=[obj.guid]), obj.title)
    preview_email.allow_tags = True
    preview_email.short_description = _('Preview Email')

    def resend(self, request, queryset):
        for q in queryset:
            print(q.resend())
    resend.short_description = _("Resend the selected emails")

    def has_change_permission(self, request, obj=None):
        return obj is None

    def __init__(self, *args, **kwargs):
        super(NoticeEmailAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

# admin.site.register(NoticeType, NoticeTypeAdmin)
# admin.site.register(NoticeSetting, NoticeSettingAdmin)
# admin.site.register(Notice, NoticeAdmin)
# admin.site.register(ObservedItem)
admin.site.register(NoticeEmail, NoticeEmailAdmin)
